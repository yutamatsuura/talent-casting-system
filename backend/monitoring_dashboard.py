#!/usr/bin/env python3
"""
リアルタイムパフォーマンス監視ダッシュボード
チューニング効果をリアルタイムで可視化
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import psutil
import asyncpg
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """パフォーマンス監視クラス"""

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.metrics_history: List[Dict[str, Any]] = []
        self.alert_thresholds = {
            "response_time": 3.0,  # 3秒
            "cpu_usage": 80.0,     # 80%
            "memory_usage": 85.0,  # 85%
            "active_connections": 20  # 20接続
        }

    async def collect_metrics(self) -> Dict[str, Any]:
        """システムメトリクス収集"""
        try:
            # システムリソース
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # データベース接続数
            try:
                conn = await asyncpg.connect(self.db_url)
                db_stats = await conn.fetchrow("""
                    SELECT
                        (SELECT count(*) FROM pg_stat_activity) as active_connections,
                        (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_queries
                """)
                await conn.close()

                active_connections = db_stats['active_connections']
                active_queries = db_stats['active_queries']
            except Exception as e:
                logger.warning(f"DB統計取得失敗: {e}")
                active_connections = 0
                active_queries = 0

            # メトリクス構築
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_usage": disk.percent
                },
                "database": {
                    "active_connections": active_connections,
                    "active_queries": active_queries
                },
                "alerts": self._generate_alerts(cpu_usage, memory.percent, active_connections)
            }

            # 履歴保存（最新100件）
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 100:
                self.metrics_history.pop(0)

            return metrics

        except Exception as e:
            logger.error(f"メトリクス収集エラー: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def _generate_alerts(self, cpu: float, memory: float, connections: int) -> List[Dict[str, str]]:
        """アラート生成"""
        alerts = []

        if cpu > self.alert_thresholds["cpu_usage"]:
            alerts.append({
                "level": "warning",
                "type": "cpu",
                "message": f"CPU使用率高: {cpu:.1f}%",
                "recommendation": "プロセス最適化またはスケールアップ検討"
            })

        if memory > self.alert_thresholds["memory_usage"]:
            alerts.append({
                "level": "warning",
                "type": "memory",
                "message": f"メモリ使用率高: {memory:.1f}%",
                "recommendation": "メモリリーク確認またはキャッシュ最適化"
            })

        if connections > self.alert_thresholds["active_connections"]:
            alerts.append({
                "level": "critical",
                "type": "database",
                "message": f"DB接続数過多: {connections}",
                "recommendation": "接続プール設定見直し"
            })

        return alerts

    def get_performance_trend(self, minutes: int = 30) -> Dict[str, Any]:
        """パフォーマンストレンド分析"""
        if not self.metrics_history:
            return {"error": "データ不足"}

        # 指定時間内のデータ抽出
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]

        if not recent_metrics:
            return {"error": "期間内データなし"}

        # トレンド分析
        cpu_values = [m["system"]["cpu_usage"] for m in recent_metrics]
        memory_values = [m["system"]["memory_usage"] for m in recent_metrics]
        connection_values = [m["database"]["active_connections"] for m in recent_metrics]

        return {
            "period_minutes": minutes,
            "sample_count": len(recent_metrics),
            "cpu_trend": {
                "current": cpu_values[-1] if cpu_values else 0,
                "average": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "peak": max(cpu_values) if cpu_values else 0,
                "trend": "increasing" if len(cpu_values) > 1 and cpu_values[-1] > cpu_values[0] else "stable"
            },
            "memory_trend": {
                "current": memory_values[-1] if memory_values else 0,
                "average": sum(memory_values) / len(memory_values) if memory_values else 0,
                "peak": max(memory_values) if memory_values else 0,
                "trend": "increasing" if len(memory_values) > 1 and memory_values[-1] > memory_values[0] else "stable"
            },
            "database_trend": {
                "current_connections": connection_values[-1] if connection_values else 0,
                "average_connections": sum(connection_values) / len(connection_values) if connection_values else 0,
                "peak_connections": max(connection_values) if connection_values else 0
            }
        }

# FastAPI アプリケーション
app = FastAPI(title="パフォーマンス監視ダッシュボード")

# グローバル監視インスタンス
monitor = None

@app.on_event("startup")
async def startup_event():
    global monitor
    # 環境変数から DB URL を取得（実際の環境に合わせて調整）
    db_url = "postgresql://user:password@localhost:5432/talent_casting"
    monitor = PerformanceMonitor(db_url)

    # 定期的なメトリクス収集開始
    asyncio.create_task(periodic_metrics_collection())

async def periodic_metrics_collection():
    """定期的なメトリクス収集"""
    while True:
        try:
            await monitor.collect_metrics()
            await asyncio.sleep(10)  # 10秒間隔
        except Exception as e:
            logger.error(f"定期収集エラー: {e}")
            await asyncio.sleep(30)

@app.get("/", response_class=HTMLResponse)
async def dashboard_page():
    """ダッシュボードHTML"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>タレントキャスティング パフォーマンス監視</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric-value { font-size: 2em; font-weight: bold; margin: 10px 0; }
            .metric-label { color: #666; font-size: 0.9em; }
            .alert { padding: 10px; margin: 10px 0; border-radius: 4px; }
            .alert.warning { background: #fff3cd; border: 1px solid #ffeaa7; }
            .alert.critical { background: #f8d7da; border: 1px solid #f5c6cb; }
            .chart-container { width: 100%; height: 300px; margin: 20px 0; }
            .status-good { color: #28a745; }
            .status-warning { color: #ffc107; }
            .status-critical { color: #dc3545; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 タレントキャスティングシステム 監視ダッシュボード</h1>
                <p>リアルタイムパフォーマンス監視 | 最終更新: <span id="lastUpdate">-</span></p>
            </div>

            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">CPU使用率</div>
                    <div class="metric-value" id="cpuUsage">-</div>
                    <div class="chart-container">
                        <canvas id="cpuChart"></canvas>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-label">メモリ使用率</div>
                    <div class="metric-value" id="memoryUsage">-</div>
                    <div class="chart-container">
                        <canvas id="memoryChart"></canvas>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-label">DB接続数</div>
                    <div class="metric-value" id="dbConnections">-</div>
                    <div class="chart-container">
                        <canvas id="dbChart"></canvas>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-label">システムアラート</div>
                    <div id="alerts">システム正常</div>
                </div>
            </div>

            <div class="metric-card">
                <h3>📊 パフォーマンストレンド (過去30分)</h3>
                <div id="trendAnalysis">データ読み込み中...</div>
            </div>
        </div>

        <script>
            // WebSocket接続
            const ws = new WebSocket('ws://localhost:8433/ws');

            // チャート初期化
            const cpuChart = new Chart(document.getElementById('cpuChart'), {
                type: 'line',
                data: { labels: [], datasets: [{ label: 'CPU %', data: [], borderColor: 'rgb(75, 192, 192)' }] },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 100 } } }
            });

            const memoryChart = new Chart(document.getElementById('memoryChart'), {
                type: 'line',
                data: { labels: [], datasets: [{ label: 'Memory %', data: [], borderColor: 'rgb(255, 99, 132)' }] },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 100 } } }
            });

            const dbChart = new Chart(document.getElementById('dbChart'), {
                type: 'line',
                data: { labels: [], datasets: [{ label: 'Connections', data: [], borderColor: 'rgb(54, 162, 235)' }] },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
            });

            // データ更新
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };

            function updateDashboard(data) {
                // 基本メトリクス更新
                document.getElementById('cpuUsage').textContent = data.system.cpu_usage.toFixed(1) + '%';
                document.getElementById('memoryUsage').textContent = data.system.memory_usage.toFixed(1) + '%';
                document.getElementById('dbConnections').textContent = data.database.active_connections;
                document.getElementById('lastUpdate').textContent = new Date(data.timestamp).toLocaleTimeString();

                // アラート更新
                const alertsDiv = document.getElementById('alerts');
                if (data.alerts.length > 0) {
                    alertsDiv.innerHTML = data.alerts.map(alert =>
                        `<div class="alert ${alert.level}"><strong>${alert.message}</strong><br>${alert.recommendation}</div>`
                    ).join('');
                } else {
                    alertsDiv.innerHTML = '<div class="status-good">✅ システム正常</div>';
                }

                // チャート更新
                const timestamp = new Date(data.timestamp).toLocaleTimeString();
                updateChart(cpuChart, timestamp, data.system.cpu_usage);
                updateChart(memoryChart, timestamp, data.system.memory_usage);
                updateChart(dbChart, timestamp, data.database.active_connections);
            }

            function updateChart(chart, label, value) {
                chart.data.labels.push(label);
                chart.data.datasets[0].data.push(value);

                // 最新50件に制限
                if (chart.data.labels.length > 50) {
                    chart.data.labels.shift();
                    chart.data.datasets[0].data.shift();
                }

                chart.update('none');
            }

            // トレンド分析更新
            setInterval(async () => {
                try {
                    const response = await fetch('/api/trend');
                    const trend = await response.json();
                    updateTrendAnalysis(trend);
                } catch (error) {
                    console.error('トレンド取得エラー:', error);
                }
            }, 30000); // 30秒間隔

            function updateTrendAnalysis(trend) {
                const trendDiv = document.getElementById('trendAnalysis');
                trendDiv.innerHTML = `
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                        <div>
                            <h4>CPU トレンド</h4>
                            <p>現在: ${trend.cpu_trend.current.toFixed(1)}%</p>
                            <p>平均: ${trend.cpu_trend.average.toFixed(1)}%</p>
                            <p>傾向: ${trend.cpu_trend.trend}</p>
                        </div>
                        <div>
                            <h4>メモリ トレンド</h4>
                            <p>現在: ${trend.memory_trend.current.toFixed(1)}%</p>
                            <p>平均: ${trend.memory_trend.average.toFixed(1)}%</p>
                            <p>傾向: ${trend.memory_trend.trend}</p>
                        </div>
                        <div>
                            <h4>DB接続 トレンド</h4>
                            <p>現在: ${trend.database_trend.current_connections}</p>
                            <p>平均: ${trend.database_trend.average_connections.toFixed(1)}</p>
                            <p>ピーク: ${trend.database_trend.peak_connections}</p>
                        </div>
                    </div>
                `;
            }
        </script>
    </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket接続"""
    await websocket.accept()
    try:
        while True:
            metrics = await monitor.collect_metrics()
            await websocket.send_text(json.dumps(metrics))
            await asyncio.sleep(10)
    except Exception as e:
        logger.error(f"WebSocket エラー: {e}")

@app.get("/api/metrics")
async def get_current_metrics():
    """現在のメトリクス取得"""
    return await monitor.collect_metrics()

@app.get("/api/trend")
async def get_performance_trend():
    """パフォーマンストレンド取得"""
    return monitor.get_performance_trend()

@app.get("/api/history")
async def get_metrics_history():
    """メトリクス履歴取得"""
    return {"history": monitor.metrics_history}

if __name__ == "__main__":
    import uvicorn
    print("🖥️ 監視ダッシュボード起動中...")
    print("📊 ダッシュボード: http://localhost:8433")
    uvicorn.run(app, host="0.0.0.0", port=8433)