#!/usr/bin/env python3
"""
タレントキャスティングシステム 効率的パフォーマンステストスイート
自動化されたベンチマーク・チューニング支援ツール
"""

import asyncio
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging
from dataclasses import dataclass
import psutil
import requests

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    """テストケース定義"""
    name: str
    company_name: str
    industry: str
    target_segments: str
    purpose: str
    budget: str
    email: str
    expected_min_results: int = 20

@dataclass
class PerformanceMetrics:
    """パフォーマンスメトリクス"""
    response_time: float
    cpu_usage_before: float
    cpu_usage_after: float
    memory_usage_before: float
    memory_usage_after: float
    result_count: int
    top_3_talents: List[Dict]

class TuningTestSuite:
    """チューニングテストスイート"""

    def __init__(self, api_base_url: str = "http://localhost:8432"):
        self.api_base_url = api_base_url
        self.test_cases = self._define_test_cases()

    def _define_test_cases(self) -> List[TestCase]:
        """代表的なテストケースを定義"""
        return [
            # 高負荷ケース：人気業界 × 人気ターゲット
            TestCase(
                name="高負荷_化粧品_女性20-34",
                company_name="株式会社テストビューティー",
                industry="化粧品・ヘアケア・オーラルケア",
                target_segments="女性20-34歳",
                purpose="ブランドの認知度向上のため",
                budget="3,000万円〜1億円未満",
                email="test@beauty-test.com"
            ),

            # 中負荷ケース：一般的な組み合わせ
            TestCase(
                name="中負荷_食品_女性35-49",
                company_name="株式会社テストフード",
                industry="食品",
                target_segments="女性35-49歳",
                purpose="新商品のプロモーションのため",
                budget="1,000万円〜3,000万円未満",
                email="test@food-test.com"
            ),

            # 低負荷ケース：ニッチな組み合わせ
            TestCase(
                name="低負荷_金融_男性50-69",
                company_name="株式会社テストファイナンス",
                industry="金融・不動産",
                target_segments="男性50-69歳",
                purpose="信頼性向上のため",
                budget="1,000万円未満",
                email="test@finance-test.com"
            ),

            # 極限ケース：複数ターゲット
            TestCase(
                name="複雑_自動車_複数ターゲット",
                company_name="株式会社テストオート",
                industry="自動車関連",
                target_segments="男性35-49歳",
                purpose="ブランドイメージ向上のため",
                budget="1億円以上",
                email="test@auto-test.com"
            )
        ]

    async def run_single_test(self, test_case: TestCase) -> PerformanceMetrics:
        """単一テストケースの実行"""
        logger.info(f"🧪 テスト開始: {test_case.name}")

        # システムリソース測定（開始前）
        cpu_before = psutil.cpu_percent(interval=0.1)
        memory_before = psutil.virtual_memory().percent

        # API呼び出し
        start_time = time.time()

        payload = {
            "company_name": test_case.company_name,
            "industry": test_case.industry,
            "target_segments": test_case.target_segments,
            "purpose": test_case.purpose,
            "budget": test_case.budget,
            "email": test_case.email
        }

        try:
            response = requests.post(
                f"{self.api_base_url}/api/matching",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result_data = response.json()

            end_time = time.time()
            response_time = end_time - start_time

            # システムリソース測定（終了後）
            cpu_after = psutil.cpu_percent(interval=0.1)
            memory_after = psutil.virtual_memory().percent

            # 結果解析
            results = result_data.get('results', [])
            top_3_talents = results[:3] if results else []

            metrics = PerformanceMetrics(
                response_time=response_time,
                cpu_usage_before=cpu_before,
                cpu_usage_after=cpu_after,
                memory_usage_before=memory_before,
                memory_usage_after=memory_after,
                result_count=len(results),
                top_3_talents=top_3_talents
            )

            logger.info(f"✅ {test_case.name}: {response_time:.3f}秒, {len(results)}件")
            return metrics

        except Exception as e:
            logger.error(f"❌ テストエラー {test_case.name}: {str(e)}")
            raise

    async def run_benchmark_suite(self, iterations: int = 5) -> Dict[str, Any]:
        """ベンチマークスイート実行"""
        logger.info(f"🚀 ベンチマークスイート開始 ({iterations}回実行)")

        all_results = {}

        for test_case in self.test_cases:
            logger.info(f"📊 {test_case.name} を {iterations}回実行中...")

            metrics_list = []
            for i in range(iterations):
                try:
                    await asyncio.sleep(1)  # API負荷軽減
                    metrics = await self.run_single_test(test_case)
                    metrics_list.append(metrics)
                    logger.info(f"  試行 {i+1}/{iterations}: {metrics.response_time:.3f}秒")
                except Exception as e:
                    logger.warning(f"  試行 {i+1}/{iterations} 失敗: {str(e)}")
                    continue

            if metrics_list:
                # 統計計算
                response_times = [m.response_time for m in metrics_list]
                result_counts = [m.result_count for m in metrics_list]

                all_results[test_case.name] = {
                    "test_case": test_case.__dict__,
                    "iterations": len(metrics_list),
                    "performance": {
                        "avg_response_time": statistics.mean(response_times),
                        "min_response_time": min(response_times),
                        "max_response_time": max(response_times),
                        "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                        "percentile_95": sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0
                    },
                    "consistency": {
                        "avg_result_count": statistics.mean(result_counts),
                        "result_count_variance": statistics.variance(result_counts) if len(result_counts) > 1 else 0,
                        "top_talent_consistency": self._check_consistency([m.top_3_talents for m in metrics_list])
                    },
                    "raw_metrics": [
                        {
                            "response_time": m.response_time,
                            "result_count": m.result_count,
                            "cpu_usage_delta": m.cpu_usage_after - m.cpu_usage_before,
                            "memory_usage_delta": m.memory_usage_after - m.memory_usage_before
                        } for m in metrics_list
                    ]
                }

        # 総合レポート生成
        benchmark_report = {
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "suite_type": "comprehensive_benchmark",
            "total_tests": len(self.test_cases),
            "total_iterations": sum(result.get("iterations", 0) for result in all_results.values()),
            "results": all_results,
            "summary": self._generate_summary(all_results),
            "recommendations": self._generate_recommendations(all_results)
        }

        # ファイル出力
        output_file = f"benchmark_comprehensive_{benchmark_report['timestamp']}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(benchmark_report, f, ensure_ascii=False, indent=2)

        logger.info(f"📋 ベンチマーク完了: {output_file}")
        return benchmark_report

    def _check_consistency(self, top_talents_list: List[List[Dict]]) -> Dict[str, Any]:
        """トップタレント一貫性チェック"""
        if not top_talents_list:
            return {"consistency_score": 0, "note": "データなし"}

        # 1位タレントの一貫性
        first_place_talents = [talents[0]['name'] if talents else None for talents in top_talents_list]
        first_place_consistency = len(set(filter(None, first_place_talents))) <= 2

        # TOP3平均一貫性
        all_top3_names = []
        for talents in top_talents_list:
            all_top3_names.extend([t['name'] for t in talents[:3]])

        unique_top3 = len(set(all_top3_names))
        total_appearances = len(all_top3_names)

        return {
            "first_place_consistent": first_place_consistency,
            "unique_top3_talents": unique_top3,
            "total_top3_appearances": total_appearances,
            "consistency_score": (total_appearances - unique_top3) / max(total_appearances, 1) * 100
        }

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """結果サマリー生成"""
        all_avg_times = [result["performance"]["avg_response_time"] for result in results.values()]

        return {
            "overall_avg_response_time": statistics.mean(all_avg_times) if all_avg_times else 0,
            "fastest_test_case": min(results.keys(), key=lambda x: results[x]["performance"]["avg_response_time"]) if results else None,
            "slowest_test_case": max(results.keys(), key=lambda x: results[x]["performance"]["avg_response_time"]) if results else None,
            "performance_variance": statistics.variance(all_avg_times) if len(all_avg_times) > 1 else 0,
            "total_execution_time": sum(result["performance"]["avg_response_time"] * result["iterations"] for result in results.values())
        }

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """チューニング推奨事項生成"""
        recommendations = []

        # パフォーマンス分析
        avg_times = [result["performance"]["avg_response_time"] for result in results.values()]
        if avg_times:
            max_time = max(avg_times)
            if max_time > 5.0:
                recommendations.append("⚠️ 5秒超過のケースあり - インデックス最適化検討")
            elif max_time > 3.0:
                recommendations.append("📈 3秒超過のケースあり - クエリ最適化検討")
            elif max_time < 1.0:
                recommendations.append("🚀 優秀なパフォーマンス - 現状維持推奨")

        # 一貫性分析
        consistency_scores = [
            result["consistency"].get("consistency_score", 0)
            for result in results.values()
        ]
        if consistency_scores:
            avg_consistency = statistics.mean(consistency_scores)
            if avg_consistency < 80:
                recommendations.append("🔄 結果一貫性低下 - マッチングロジック確認必要")
            elif avg_consistency > 95:
                recommendations.append("✅ 高い結果一貫性 - アルゴリズム安定")

        # バリアンス分析
        for test_name, result in results.items():
            std_dev = result["performance"]["std_dev"]
            avg_time = result["performance"]["avg_response_time"]
            if avg_time > 0 and (std_dev / avg_time) > 0.3:
                recommendations.append(f"📊 {test_name}: 実行時間のばらつき大 - 負荷分散検討")

        return recommendations

async def main():
    """メイン実行関数"""
    print("🎯 タレントキャスティングシステム チューニング効率化ツール")
    print("=" * 60)

    # テストスイート初期化
    suite = TuningTestSuite()

    # ベンチマーク実行
    try:
        report = await suite.run_benchmark_suite(iterations=3)

        # 結果表示
        print("\n📊 実行結果サマリー:")
        print("-" * 40)
        summary = report["summary"]
        print(f"平均レスポンス時間: {summary['overall_avg_response_time']:.3f}秒")
        print(f"最速ケース: {summary['fastest_test_case']}")
        print(f"最遅ケース: {summary['slowest_test_case']}")

        print("\n💡 チューニング推奨事項:")
        print("-" * 40)
        for rec in report["recommendations"]:
            print(f"  {rec}")

        print(f"\n📋 詳細レポート: benchmark_comprehensive_{report['timestamp']}.json")

    except Exception as e:
        logger.error(f"❌ テスト実行エラー: {str(e)}")
        print(f"エラー: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())