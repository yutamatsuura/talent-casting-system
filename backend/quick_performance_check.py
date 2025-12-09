#!/usr/bin/env python3
"""
クイックパフォーマンスチェック
日常的なチューニング作業用の軽量テスト
"""

import time
import json
import statistics
import requests
from datetime import datetime
from typing import Dict, Any, List

class QuickPerformanceCheck:
    """軽量パフォーマンスチェッククラス"""

    def __init__(self, api_base_url: str = "http://localhost:8432"):
        self.api_base_url = api_base_url

    def test_single_scenario(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """単一シナリオの高速テスト"""
        print(f"⚡ クイックテスト実行: {payload['company_name']}")

        response_times = []
        result_counts = []

        # 3回実行（軽量）
        for i in range(3):
            start_time = time.time()

            try:
                response = requests.post(
                    f"{self.api_base_url}/api/matching",
                    json=payload,
                    timeout=15
                )
                response.raise_for_status()
                result_data = response.json()

                end_time = time.time()
                response_time = end_time - start_time

                response_times.append(response_time)
                result_counts.append(len(result_data.get('results', [])))

                print(f"  試行 {i+1}: {response_time:.3f}秒, {result_counts[-1]}件")

            except Exception as e:
                print(f"  試行 {i+1}: エラー - {str(e)}")
                continue

            time.sleep(0.5)  # 短いインターバル

        if not response_times:
            return {"error": "全ての試行が失敗"}

        # 結果集計
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        avg_results = statistics.mean(result_counts)

        # 評価
        performance_grade = self._grade_performance(avg_time, max_time)

        return {
            "avg_response_time": avg_time,
            "max_response_time": max_time,
            "avg_result_count": avg_results,
            "performance_grade": performance_grade,
            "samples": len(response_times)
        }

    def _grade_performance(self, avg_time: float, max_time: float) -> Dict[str, str]:
        """パフォーマンス評価"""
        if avg_time <= 1.0 and max_time <= 2.0:
            return {"grade": "A", "status": "優秀", "emoji": "🚀"}
        elif avg_time <= 2.0 and max_time <= 3.0:
            return {"grade": "B", "status": "良好", "emoji": "✅"}
        elif avg_time <= 3.0 and max_time <= 5.0:
            return {"grade": "C", "status": "普通", "emoji": "⚠️"}
        else:
            return {"grade": "D", "status": "要改善", "emoji": "❌"}

    def run_quick_benchmark(self) -> Dict[str, Any]:
        """クイックベンチマーク実行"""
        print("🎯 クイックパフォーマンスチェック開始")
        print("-" * 50)

        # 代表的なテストケース（軽量版）
        test_cases = [
            {
                "name": "人気ケース",
                "payload": {
                    "company_name": "株式会社テストビューティー",
                    "industry": "化粧品・ヘアケア・オーラルケア",
                    "target_segments": "女性20-34歳",
                    "purpose": "ブランドの認知度向上のため",
                    "budget": "3,000万円〜1億円未満",
                    "email": "test@beauty-test.com"
                }
            },
            {
                "name": "一般ケース",
                "payload": {
                    "company_name": "株式会社テストフード",
                    "industry": "食品",
                    "target_segments": "女性35-49歳",
                    "purpose": "新商品のプロモーションのため",
                    "budget": "1,000万円〜3,000万円未満",
                    "email": "test@food-test.com"
                }
            }
        ]

        results = {}
        overall_times = []

        for test_case in test_cases:
            result = self.test_single_scenario(test_case["payload"])
            results[test_case["name"]] = result

            if "avg_response_time" in result:
                overall_times.append(result["avg_response_time"])

        # 総合評価
        if overall_times:
            overall_avg = statistics.mean(overall_times)
            overall_grade = self._grade_performance(overall_avg, max(overall_times))
        else:
            overall_avg = 0
            overall_grade = {"grade": "F", "status": "測定不能", "emoji": "💥"}

        summary = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "overall_avg_time": overall_avg,
            "overall_grade": overall_grade,
            "test_results": results,
            "recommendation": self._generate_quick_recommendation(results)
        }

        return summary

    def _generate_quick_recommendation(self, results: Dict[str, Any]) -> str:
        """クイック推奨事項生成"""
        avg_times = []
        for test_name, result in results.items():
            if "avg_response_time" in result:
                avg_times.append(result["avg_response_time"])

        if not avg_times:
            return "❌ テストが失敗しました - サーバー接続を確認してください"

        max_time = max(avg_times)
        avg_time = statistics.mean(avg_times)

        if max_time > 5.0:
            return "🔧 緊急: 5秒超過 - インデックス最適化またはクエリチューニング必須"
        elif max_time > 3.0:
            return "📈 改善推奨: 3秒超過 - SQLクエリの最適化を検討"
        elif avg_time < 1.0:
            return "🚀 優秀なパフォーマンス - 現状維持で問題なし"
        elif avg_time < 2.0:
            return "✅ 良好なパフォーマンス - 軽微な最適化で更なる向上可能"
        else:
            return "⚡ 標準的パフォーマンス - 継続的な監視推奨"

def main():
    """メイン実行"""
    checker = QuickPerformanceCheck()

    try:
        # ヘルスチェック
        health_response = requests.get(f"{checker.api_base_url}/api/health", timeout=5)
        health_response.raise_for_status()
        print("✅ APIサーバー接続確認完了")

    except Exception as e:
        print(f"❌ APIサーバー接続失敗: {e}")
        print("💡 解決方法: uvicorn app.main:app --host 0.0.0.0 --port 8432")
        return

    # クイックテスト実行
    results = checker.run_quick_benchmark()

    # 結果表示
    print("\n" + "=" * 60)
    print("📊 クイックパフォーマンス結果")
    print("=" * 60)

    overall_grade = results["overall_grade"]
    print(f"🏆 総合評価: {overall_grade['emoji']} {overall_grade['grade']}グレード ({overall_grade['status']})")
    print(f"⏱️ 平均レスポンス時間: {results['overall_avg_time']:.3f}秒")

    print(f"\n💡 推奨アクション:")
    print(f"   {results['recommendation']}")

    print(f"\n📋 詳細結果:")
    for test_name, result in results["test_results"].items():
        if "performance_grade" in result:
            grade = result["performance_grade"]
            print(f"   {test_name}: {grade['emoji']} {result['avg_response_time']:.3f}秒 ({grade['status']})")

    # ファイル出力
    output_file = f"quick_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 詳細結果: {output_file}")
    print("\n🔄 定期実行推奨: 機能変更後、毎日定時、デプロイ前")

if __name__ == "__main__":
    main()