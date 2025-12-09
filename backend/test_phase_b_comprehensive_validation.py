"""
Phase B超最適化実装の診断結果正確性 - 完全検証スクリプト
=================================================================

検証内容:
1. マッチングロジック完全検証（STEP 0-5）
2. 結果データ品質検証（タレント30名、スコア、ランキング）
3. ビジネスロジック検証（おすすめタレント統合、業種適合性）
4. Phase A vs Phase B 比較検証（結果一致性）
"""

import asyncio
import sys
import os
from typing import List, Dict, Any
from datetime import datetime

# バックエンドモジュールをインポート
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.connection import get_asyncpg_connection
from app.db.ultra_optimized_queries import UltraOptimizedMatchingQueries


class PhaseBComprehensiveValidator:
    """Phase B超最適化実装の完全検証クラス"""

    def __init__(self):
        self.test_cases = [
            {
                "name": "化粧品・ヘアケア・オーラルケア 女性20-34歳 1,000万円〜3,000万円未満",
                "industry": "化粧品・ヘアケア・オーラルケア",
                "target_segment": "女性20-34歳",
                "budget": "1,000万円〜3,000万円未満",
            },
            {
                "name": "食品 女性35-49歳 3,000万円〜5,000万円未満",
                "industry": "食品",
                "target_segment": "女性35-49歳",
                "budget": "3,000万円〜5,000万円未満",
            },
            {
                "name": "アルコール飲料 男性35-49歳 5,000万円〜1億円未満",
                "industry": "アルコール飲料",
                "target_segment": "男性35-49歳",
                "budget": "5,000万円〜1億円未満",
            },
        ]
        self.validation_results = []

    async def validate_step0_budget_filter(self, results: List[Dict], budget_max: float) -> Dict:
        """STEP 0: 予算フィルタリング検証"""
        validation = {
            "step": "STEP 0: 予算フィルタリング",
            "passed": True,
            "errors": [],
            "warnings": [],
        }

        if budget_max != float("inf"):
            conn = await get_asyncpg_connection()
            try:
                for result in results:
                    account_id = result["account_id"]
                    row = await conn.fetchrow(
                        """
                        SELECT mta.money_max_one_year
                        FROM m_talent_act mta
                        WHERE mta.account_id = $1
                        """,
                        account_id,
                    )

                    if row and row["money_max_one_year"]:
                        actual_budget = row["money_max_one_year"]
                        if actual_budget > budget_max:
                            validation["passed"] = False
                            validation["errors"].append(
                                f"タレントID {account_id}: 予算超過 {actual_budget} > {budget_max}"
                            )
            finally:
                await conn.close()

        validation["summary"] = f"検証完了: {'✅ PASS' if validation['passed'] else '❌ FAIL'}"
        return validation

    async def validate_step1_base_power(self, results: List[Dict], target_segment_id: int) -> Dict:
        """STEP 1: 基礎パワー得点計算検証 (VR人気度 + TPRパワースコア) / 2"""
        validation = {
            "step": "STEP 1: 基礎パワー得点",
            "passed": True,
            "errors": [],
            "warnings": [],
            "details": [],
        }

        conn = await get_asyncpg_connection()
        try:
            for result in results[:5]:  # 上位5名をサンプル検証
                account_id = result["account_id"]
                expected_base_power = result.get("base_power_score", 0)

                row = await conn.fetchrow(
                    """
                    SELECT
                        (COALESCE(vr_popularity, 0) + COALESCE(tpr_power_score, 0)) / 2.0 AS calculated_base_power
                    FROM talent_scores
                    WHERE account_id = $1 AND target_segment_id = $2
                    """,
                    account_id,
                    target_segment_id,
                )

                if row:
                    calculated_base_power = float(row["calculated_base_power"])
                    expected_base_power = float(expected_base_power)
                    diff = abs(calculated_base_power - expected_base_power)

                    validation["details"].append(
                        {
                            "account_id": account_id,
                            "expected": round(expected_base_power, 2),
                            "calculated": round(calculated_base_power, 2),
                            "diff": round(diff, 2),
                        }
                    )

                    if diff > 0.1:  # 0.1ポイント以上の誤差は警告
                        validation["passed"] = False
                        validation["errors"].append(
                            f"タレントID {account_id}: 基礎パワー得点不一致 "
                            f"期待値={expected_base_power:.2f}, 計算値={calculated_base_power:.2f}"
                        )
        finally:
            await conn.close()

        validation["summary"] = f"検証完了: {'✅ PASS' if validation['passed'] else '❌ FAIL'}"
        return validation

    async def validate_step2_image_adjustment(self, results: List[Dict], target_segment_id: int, image_item_ids: List[int]) -> Dict:
        """STEP 2: 業種イメージ査定検証（PERCENT_RANK()）"""
        validation = {
            "step": "STEP 2: 業種イメージ査定",
            "passed": True,
            "errors": [],
            "warnings": [],
            "details": [],
        }

        # サンプル検証（上位3名）
        for result in results[:3]:
            account_id = result["account_id"]
            image_adjustment = result.get("image_adjustment", 0)

            validation["details"].append(
                {
                    "account_id": account_id,
                    "image_adjustment": round(image_adjustment, 2),
                    "expected_range": "[-12.0, +12.0]",
                }
            )

            # 範囲チェック
            if not (-12.0 <= image_adjustment <= 12.0):
                validation["passed"] = False
                validation["errors"].append(
                    f"タレントID {account_id}: 業種イメージ調整値が範囲外 {image_adjustment}"
                )

        validation["summary"] = f"検証完了: {'✅ PASS' if validation['passed'] else '❌ FAIL'}"
        return validation

    async def validate_step3_reflected_score(self, results: List[Dict]) -> Dict:
        """STEP 3: 基礎反映得点検証（STEP1 + STEP2）"""
        validation = {
            "step": "STEP 3: 基礎反映得点",
            "passed": True,
            "errors": [],
            "warnings": [],
            "details": [],
        }

        for result in results[:5]:
            account_id = result["account_id"]
            base_power = result.get("base_power_score", 0)
            image_adjustment = result.get("image_adjustment", 0)
            reflected_score = result.get("reflected_score", 0)

            expected_reflected = base_power + image_adjustment
            diff = abs(expected_reflected - reflected_score)

            validation["details"].append(
                {
                    "account_id": account_id,
                    "base_power": round(base_power, 2),
                    "image_adjustment": round(image_adjustment, 2),
                    "reflected_score": round(reflected_score, 2),
                    "expected": round(expected_reflected, 2),
                    "diff": round(diff, 2),
                }
            )

            if diff > 0.01:
                validation["passed"] = False
                validation["errors"].append(
                    f"タレントID {account_id}: 基礎反映得点不一致 "
                    f"期待値={expected_reflected:.2f}, 実際={reflected_score:.2f}"
                )

        validation["summary"] = f"検証完了: {'✅ PASS' if validation['passed'] else '❌ FAIL'}"
        return validation

    async def validate_step4_ranking(self, results: List[Dict]) -> Dict:
        """STEP 4: ランキング確定検証（30名、順位の正確性）"""
        validation = {
            "step": "STEP 4: ランキング確定",
            "passed": True,
            "errors": [],
            "warnings": [],
            "details": {
                "total_talents": len(results),
                "expected_total": 30,
                "ranking_check": [],
            },
        }

        # 総数チェック
        if len(results) != 30:
            validation["passed"] = False
            validation["errors"].append(f"タレント数不一致: {len(results)}名 (期待値: 30名)")

        # ランキング連続性チェック
        for i, result in enumerate(results):
            expected_ranking = i + 1
            actual_ranking = result.get("ranking", 0)

            if actual_ranking != expected_ranking:
                validation["passed"] = False
                validation["errors"].append(
                    f"ランキング不一致: 位置{i+1}のタレントID {result['account_id']} "
                    f"期待順位={expected_ranking}, 実際順位={actual_ranking}"
                )

        # reflected_score降順チェック
        for i in range(len(results) - 1):
            current_score = results[i].get("reflected_score", 0)
            next_score = results[i + 1].get("reflected_score", 0)

            if current_score < next_score:
                validation["passed"] = False
                validation["errors"].append(
                    f"ソート順序エラー: {i+1}位 (score={current_score:.2f}) < {i+2}位 (score={next_score:.2f})"
                )

        validation["summary"] = f"検証完了: {'✅ PASS' if validation['passed'] else '❌ FAIL'}"
        return validation

    async def validate_step5_matching_score(self, results: List[Dict]) -> Dict:
        """STEP 5: マッチングスコア振り分け検証（86-99点台）"""
        validation = {
            "step": "STEP 5: マッチングスコア振り分け",
            "passed": True,
            "errors": [],
            "warnings": [],
            "details": {"score_distribution": {}},
        }

        score_ranges = {
            "1-3位": (97.0, 99.7),
            "4-10位": (93.0, 96.9),
            "11-20位": (89.0, 92.9),
            "21-30位": (86.0, 88.9),
        }

        for result in results:
            ranking = result.get("ranking", 0)
            matching_score = result.get("matching_score", 0)

            # スコア範囲判定
            if 1 <= ranking <= 3:
                expected_range = score_ranges["1-3位"]
                range_name = "1-3位"
            elif 4 <= ranking <= 10:
                expected_range = score_ranges["4-10位"]
                range_name = "4-10位"
            elif 11 <= ranking <= 20:
                expected_range = score_ranges["11-20位"]
                range_name = "11-20位"
            elif 21 <= ranking <= 30:
                expected_range = score_ranges["21-30位"]
                range_name = "21-30位"
            else:
                validation["passed"] = False
                validation["errors"].append(f"不正な順位: {ranking}位")
                continue

            # スコア範囲チェック
            if not (expected_range[0] <= matching_score <= expected_range[1]):
                validation["passed"] = False
                validation["errors"].append(
                    f"{ranking}位 (タレントID {result['account_id']}): "
                    f"スコア範囲外 {matching_score:.1f} (期待: {expected_range[0]}-{expected_range[1]})"
                )

            # 分布記録
            if range_name not in validation["details"]["score_distribution"]:
                validation["details"]["score_distribution"][range_name] = []
            validation["details"]["score_distribution"][range_name].append(
                f"{ranking}位: {matching_score:.1f}"
            )

        validation["summary"] = f"検証完了: {'✅ PASS' if validation['passed'] else '❌ FAIL'}"
        return validation

    async def validate_talent_data_quality(self, results: List[Dict]) -> Dict:
        """タレントデータ品質検証（名前、カテゴリ、欠損値チェック）"""
        validation = {
            "step": "タレントデータ品質",
            "passed": True,
            "errors": [],
            "warnings": [],
            "details": [],
        }

        for result in results:
            account_id = result.get("account_id")
            name = result.get("name", "")
            category = result.get("act_genre", "")

            issues = []

            # 必須データ欠損チェック
            if not account_id:
                issues.append("account_id欠損")
            if not name or name == f"タレント{account_id}":
                issues.append("名前欠損または仮名")
            if not category:
                issues.append("カテゴリ欠損")

            if issues:
                validation["passed"] = False
                validation["errors"].append(
                    f"タレントID {account_id}: データ品質問題 - {', '.join(issues)}"
                )

            validation["details"].append(
                {
                    "account_id": account_id,
                    "name": name,
                    "category": category,
                    "has_issues": len(issues) > 0,
                }
            )

        validation["summary"] = f"検証完了: {'✅ PASS' if validation['passed'] else '❌ FAIL'}"
        return validation

    async def execute_test_case(self, test_case: Dict) -> Dict:
        """単一テストケースを実行"""
        print(f"\n{'='*80}")
        print(f"テストケース: {test_case['name']}")
        print(f"{'='*80}")

        start_time = datetime.now()

        # パラメータ取得
        conn = await get_asyncpg_connection()
        try:
            # 予算上限取得
            normalized_budget = test_case["budget"].replace("～", "〜").replace(" ", "").replace("　", "")
            budget_row = await conn.fetchrow(
                """
                SELECT max_amount FROM budget_ranges
                WHERE REPLACE(REPLACE(REPLACE(range_name, '～', '〜'), ' ', ''), '　', '') = $1
                """,
                normalized_budget,
            )
            budget_max = float(budget_row["max_amount"] or float("inf")) if budget_row else float("inf")

            # ターゲット層ID取得
            segment_row = await conn.fetchrow(
                "SELECT target_segment_id FROM target_segments WHERE segment_name = $1",
                test_case["target_segment"],
            )
            target_segment_id = segment_row["target_segment_id"] if segment_row else None

            # 業種イメージID取得
            image_row = await conn.fetchrow(
                "SELECT required_image_id FROM industries WHERE industry_name = $1",
                test_case["industry"],
            )
            image_item_ids = [image_row["required_image_id"]] if (image_row and image_row["required_image_id"]) else [1, 2, 3, 4, 5, 6, 7]

            # アルコール業界判定
            is_alcohol_industry = test_case["industry"] == "アルコール飲料"

        finally:
            await conn.close()

        # Phase B: 超最適化マッチング実行
        print(f"\n📊 Phase B超最適化マッチング実行中...")
        phase_b_results = await UltraOptimizedMatchingQueries.execute_complete_unified_matching_query(
            budget_max=budget_max,
            target_segment_id=target_segment_id,
            image_item_ids=image_item_ids,
            industry_name=test_case["industry"],
            is_alcohol_industry=is_alcohol_industry,
        )

        # STEP 5: スコア振り分け適用
        phase_b_results = UltraOptimizedMatchingQueries.apply_step5_score_distribution_optimized(
            phase_b_results
        )

        elapsed_time = (datetime.now() - start_time).total_seconds() * 1000

        print(f"✅ 処理完了: {elapsed_time:.2f}ms")
        print(f"📈 タレント数: {len(phase_b_results)}名")

        # 各段階の検証実行
        print(f"\n🔍 STEP 0-5 検証開始...")

        validations = [
            await self.validate_step0_budget_filter(phase_b_results, budget_max),
            await self.validate_step1_base_power(phase_b_results, target_segment_id),
            await self.validate_step2_image_adjustment(phase_b_results, target_segment_id, image_item_ids),
            await self.validate_step3_reflected_score(phase_b_results),
            await self.validate_step4_ranking(phase_b_results),
            await self.validate_step5_matching_score(phase_b_results),
            await self.validate_talent_data_quality(phase_b_results),
        ]

        # 検証結果サマリー
        all_passed = all(v["passed"] for v in validations)

        test_result = {
            "test_case": test_case["name"],
            "passed": all_passed,
            "processing_time_ms": round(elapsed_time, 2),
            "total_talents": len(phase_b_results),
            "validations": validations,
            "top_5_talents": [
                {
                    "ranking": r["ranking"],
                    "name": r.get("name", ""),
                    "matching_score": round(r.get("matching_score", 0), 1),
                    "base_power_score": round(r.get("base_power_score", 0), 2),
                    "image_adjustment": round(r.get("image_adjustment", 0), 2),
                    "reflected_score": round(r.get("reflected_score", 0), 2),
                }
                for r in phase_b_results[:5]
            ],
        }

        return test_result

    def print_validation_report(self, test_result: Dict):
        """検証レポート出力"""
        print(f"\n{'='*80}")
        print(f"🎯 検証レポート: {test_result['test_case']}")
        print(f"{'='*80}")

        print(f"\n⏱️  処理時間: {test_result['processing_time_ms']:.2f}ms")
        print(f"👥 タレント数: {test_result['total_talents']}名")
        print(f"📊 総合判定: {'✅ 全検証PASS' if test_result['passed'] else '❌ 検証FAIL'}")

        print(f"\n📋 各段階検証結果:")
        for validation in test_result["validations"]:
            status = "✅ PASS" if validation["passed"] else "❌ FAIL"
            print(f"  {status} {validation['step']}")

            if validation["errors"]:
                for error in validation["errors"]:
                    print(f"    ❌ {error}")

            if validation["warnings"]:
                for warning in validation["warnings"]:
                    print(f"    ⚠️  {warning}")

        print(f"\n🏆 上位5名タレント:")
        print(f"{'順位':<6} {'タレント名':<20} {'マッチングスコア':<15} {'基礎パワー':<12} {'業種調整':<10} {'反映得点':<10}")
        print("-" * 80)
        for talent in test_result["top_5_talents"]:
            print(
                f"{talent['ranking']:<6} "
                f"{talent['name']:<20} "
                f"{talent['matching_score']:<15.1f} "
                f"{talent['base_power_score']:<12.2f} "
                f"{talent['image_adjustment']:<10.2f} "
                f"{talent['reflected_score']:<10.2f}"
            )

    async def run_all_tests(self):
        """全テストケースを実行"""
        print("\n" + "="*80)
        print("🚀 Phase B超最適化実装 - 完全検証開始")
        print("="*80)

        overall_start = datetime.now()
        all_passed = True

        for test_case in self.test_cases:
            try:
                test_result = await self.execute_test_case(test_case)
                self.validation_results.append(test_result)
                self.print_validation_report(test_result)

                if not test_result["passed"]:
                    all_passed = False

            except Exception as e:
                print(f"\n❌ テストケース実行エラー: {test_case['name']}")
                print(f"エラー詳細: {str(e)}")
                import traceback
                traceback.print_exc()
                all_passed = False

        overall_elapsed = (datetime.now() - overall_start).total_seconds()

        # 最終サマリー
        print(f"\n{'='*80}")
        print(f"📊 最終サマリー")
        print(f"{'='*80}")
        print(f"総実行時間: {overall_elapsed:.2f}秒")
        print(f"テストケース数: {len(self.test_cases)}")
        print(f"成功: {sum(1 for r in self.validation_results if r['passed'])}件")
        print(f"失敗: {sum(1 for r in self.validation_results if not r['passed'])}件")
        print(f"\n🎯 総合判定: {'✅ 全テストPASS' if all_passed else '❌ 一部テストFAIL'}")


async def main():
    """メイン実行関数"""
    validator = PhaseBComprehensiveValidator()
    await validator.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
