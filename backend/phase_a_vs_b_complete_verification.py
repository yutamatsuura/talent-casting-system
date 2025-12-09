"""Phase A vs Phase B 完全性検証スクリプト
目的: Phase B超最適化版が「高速だが不完全」なのか「正しく最適化されているから高速」なのかを徹底検証
"""
import asyncio
import sys
import os
import time
import json
from typing import List, Dict, Any
from pprint import pprint

sys.path.append(os.path.dirname(__file__))

from app.db.connection import get_asyncpg_connection
from app.db.ultra_optimized_queries import UltraOptimizedMatchingQueries
from app.api.endpoints.matching import (
    execute_matching_logic,
    apply_recommended_talents_integration,
    get_matching_parameters,
)
from app.schemas.matching import MatchingFormData


async def run_phase_a_matching(
    industry: str,
    target_segment: str,
    budget_range: str
) -> tuple[List[Dict], float]:
    """Phase A（従来版）マッチング実行"""
    start_time = time.time()

    # フォームデータ作成
    form_data = MatchingFormData(
        company_name="検証用テスト会社",
        industry=industry,
        target_segments=target_segment,
        purpose="Phase A検証",
        budget=budget_range,
        email="test-phase-a@verification.local",
    )

    # Phase A: 既存ロジック実行
    max_budget, target_segment_id, image_item_ids = await get_matching_parameters(
        budget_range, target_segment, industry
    )

    # マッチングロジック実行
    talent_data = await execute_matching_logic(
        form_data, max_budget, target_segment_id, image_item_ids
    )

    # おすすめタレント統合
    integrated_results = await apply_recommended_talents_integration(
        form_data, talent_data
    )

    processing_time = (time.time() - start_time) * 1000
    return integrated_results, processing_time


async def run_phase_b_matching(
    industry: str,
    target_segment: str,
    budget_range: str
) -> tuple[List[Dict], float]:
    """Phase B（超最適化版）マッチング実行"""
    start_time = time.time()

    # Phase B: 超最適化ロジック実行
    talent_data = await UltraOptimizedMatchingQueries.execute_ultra_optimized_matching_flow(
        industry, target_segment, budget_range
    )

    processing_time = (time.time() - start_time) * 1000
    return talent_data, processing_time


def compare_results(phase_a_results: List[Dict], phase_b_results: List[Dict]) -> Dict[str, Any]:
    """Phase AとPhase Bの結果を詳細比較"""
    comparison = {
        "タレント数比較": {
            "Phase A": len(phase_a_results),
            "Phase B": len(phase_b_results),
            "一致": len(phase_a_results) == len(phase_b_results)
        },
        "データ欠損チェック": {
            "Phase A": [],
            "Phase B": []
        },
        "スコア範囲チェック": {
            "Phase A": {"最小": None, "最大": None},
            "Phase B": {"最小": None, "最大": None}
        },
        "順位帯別人数": {
            "Phase A": {"1-3位": 0, "4-10位": 0, "11-20位": 0, "21-30位": 0},
            "Phase B": {"1-3位": 0, "4-10位": 0, "11-20位": 0, "21-30位": 0}
        },
        "タレントID一致率": None,
        "詳細差異": []
    }

    # Phase A データ欠損チェック
    for i, result in enumerate(phase_a_results, 1):
        if not result.get("name"):
            comparison["データ欠損チェック"]["Phase A"].append(f"{i}位: 名前欠損")
        if not result.get("act_genre"):
            comparison["データ欠損チェック"]["Phase A"].append(f"{i}位: カテゴリ欠損")
        if result.get("matching_score") is None:
            comparison["データ欠損チェック"]["Phase A"].append(f"{i}位: スコア欠損")

    # Phase B データ欠損チェック
    for i, result in enumerate(phase_b_results, 1):
        if not result.get("name"):
            comparison["データ�損チェック"]["Phase B"].append(f"{i}位: 名前欠損")
        if not result.get("act_genre"):
            comparison["データ欠損チェック"]["Phase B"].append(f"{i}位: カテゴリ欠損")
        if result.get("matching_score") is None:
            comparison["データ欠損チェック"]["Phase B"].append(f"{i}位: スコア欠損")

    # スコア範囲チェック
    phase_a_scores = [r.get("matching_score", 0) for r in phase_a_results if r.get("matching_score")]
    phase_b_scores = [r.get("matching_score", 0) for r in phase_b_results if r.get("matching_score")]

    if phase_a_scores:
        comparison["スコア範囲チェック"]["Phase A"] = {
            "最小": min(phase_a_scores),
            "最大": max(phase_a_scores),
            "平均": sum(phase_a_scores) / len(phase_a_scores)
        }

    if phase_b_scores:
        comparison["スコア範囲チェック"]["Phase B"] = {
            "最小": min(phase_b_scores),
            "最大": max(phase_b_scores),
            "平均": sum(phase_b_scores) / len(phase_b_scores)
        }

    # 順位帯別人数
    for result in phase_a_results:
        rank = result.get("ranking", 0)
        if 1 <= rank <= 3:
            comparison["順位帯別人数"]["Phase A"]["1-3位"] += 1
        elif 4 <= rank <= 10:
            comparison["順位帯別人数"]["Phase A"]["4-10位"] += 1
        elif 11 <= rank <= 20:
            comparison["順位帯別人数"]["Phase A"]["11-20位"] += 1
        elif 21 <= rank <= 30:
            comparison["順位帯別人数"]["Phase A"]["21-30位"] += 1

    for result in phase_b_results:
        rank = result.get("ranking", 0)
        if 1 <= rank <= 3:
            comparison["順位帯別人数"]["Phase B"]["1-3位"] += 1
        elif 4 <= rank <= 10:
            comparison["順位帯別人数"]["Phase B"]["4-10位"] += 1
        elif 11 <= rank <= 20:
            comparison["順位帯別人数"]["Phase B"]["11-20位"] += 1
        elif 21 <= rank <= 30:
            comparison["順位帯別人数"]["Phase B"]["21-30位"] += 1

    # タレントID一致率
    phase_a_ids = set([r["account_id"] for r in phase_a_results])
    phase_b_ids = set([r["account_id"] for r in phase_b_results])

    common_ids = phase_a_ids & phase_b_ids
    comparison["タレントID一致率"] = {
        "共通": len(common_ids),
        "Phase A専用": len(phase_a_ids - phase_b_ids),
        "Phase B専用": len(phase_b_ids - phase_a_ids),
        "一致率": f"{len(common_ids) / max(len(phase_a_ids), len(phase_b_ids)) * 100:.1f}%"
    }

    # 詳細差異（上位10名のみ比較）
    for i in range(min(10, len(phase_a_results), len(phase_b_results))):
        phase_a = phase_a_results[i]
        phase_b = phase_b_results[i]

        if phase_a["account_id"] != phase_b["account_id"]:
            comparison["詳細差異"].append({
                "順位": i + 1,
                "Phase A": {
                    "ID": phase_a["account_id"],
                    "名前": phase_a.get("name", "N/A"),
                    "スコア": phase_a.get("matching_score", "N/A")
                },
                "Phase B": {
                    "ID": phase_b["account_id"],
                    "名前": phase_b.get("name", "N/A"),
                    "スコア": phase_b.get("matching_score", "N/A")
                }
            })

    return comparison


async def main():
    """メイン検証処理"""
    print("=" * 80)
    print("Phase A vs Phase B 完全性検証")
    print("=" * 80)

    # テストケース: 複数の条件パターンで検証
    test_cases = [
        {
            "industry": "化粧品・ヘアケア・オーラルケア",
            "target_segment": "女性20-34歳",
            "budget_range": "1,000万円〜3,000万円未満"
        },
        {
            "industry": "アルコール飲料",
            "target_segment": "男性20-34歳",
            "budget_range": "5,000万円〜1億円未満"
        },
    ]

    for idx, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"テストケース {idx}: {test_case['industry']} / {test_case['target_segment']}")
        print(f"{'=' * 80}\n")

        # Phase A実行
        print("Phase A実行中...")
        phase_a_results, phase_a_time = await run_phase_a_matching(
            test_case["industry"],
            test_case["target_segment"],
            test_case["budget_range"]
        )
        print(f"✓ Phase A完了: {phase_a_time:.2f}ms, {len(phase_a_results)}件")

        # Phase B実行
        print("Phase B実行中...")
        phase_b_results, phase_b_time = await run_phase_b_matching(
            test_case["industry"],
            test_case["target_segment"],
            test_case["budget_range"]
        )
        print(f"✓ Phase B完了: {phase_b_time:.2f}ms, {len(phase_b_results)}件")

        # 処理時間比較
        speedup = ((phase_a_time - phase_b_time) / phase_a_time) * 100
        print(f"\n⚡ 高速化率: {speedup:.1f}% (Phase A: {phase_a_time:.2f}ms → Phase B: {phase_b_time:.2f}ms)")

        # 結果比較
        print("\n📊 結果比較:")
        comparison = compare_results(phase_a_results, phase_b_results)

        print(f"\n【タレント数】")
        print(f"  Phase A: {comparison['タレント数比較']['Phase A']}件")
        print(f"  Phase B: {comparison['タレント数比較']['Phase B']}件")
        print(f"  一致: {'✓' if comparison['タレント数比較']['一致'] else '✗'}")

        print(f"\n【データ欠損チェック】")
        if comparison["データ欠損チェック"]["Phase A"]:
            print(f"  Phase A欠損: {comparison['データ欠損チェック']['Phase A']}")
        else:
            print(f"  Phase A欠損: なし ✓")

        if comparison["データ欠損チェック"]["Phase B"]:
            print(f"  Phase B欠損: {comparison['データ欠損チェック']['Phase B']}")
        else:
            print(f"  Phase B欠損: なし ✓")

        print(f"\n【スコア範囲】")
        if comparison['スコア範囲チェック']['Phase A']['最小'] is not None:
            print(f"  Phase A: {comparison['スコア範囲チェック']['Phase A']['最小']:.1f} 〜 {comparison['スコア範囲チェック']['Phase A']['最大']:.1f} (平均: {comparison['スコア範囲チェック']['Phase A']['平均']:.1f})")
        else:
            print(f"  Phase A: スコアデータなし")

        if comparison['スコア範囲チェック']['Phase B']['最小'] is not None:
            print(f"  Phase B: {comparison['スコア範囲チェック']['Phase B']['最小']:.1f} 〜 {comparison['スコア範囲チェック']['Phase B']['最大']:.1f} (平均: {comparison['スコア範囲チェック']['Phase B']['平均']:.1f})")
        else:
            print(f"  Phase B: スコアデータなし")

        print(f"\n【順位帯別人数】")
        print(f"  1-3位:   Phase A={comparison['順位帯別人数']['Phase A']['1-3位']}, Phase B={comparison['順位帯別人数']['Phase B']['1-3位']}")
        print(f"  4-10位:  Phase A={comparison['順位帯別人数']['Phase A']['4-10位']}, Phase B={comparison['順位帯別人数']['Phase B']['4-10位']}")
        print(f"  11-20位: Phase A={comparison['順位帯別人数']['Phase A']['11-20位']}, Phase B={comparison['順位帯別人数']['Phase B']['11-20位']}")
        print(f"  21-30位: Phase A={comparison['順位帯別人数']['Phase A']['21-30位']}, Phase B={comparison['順位帯別人数']['Phase B']['21-30位']}")

        print(f"\n【タレントID一致率】")
        print(f"  共通ID: {comparison['タレントID一致率']['共通']}件")
        print(f"  Phase A専用: {comparison['タレントID一致率']['Phase A専用']}件")
        print(f"  Phase B専用: {comparison['タレントID一致率']['Phase B専用']}件")
        print(f"  一致率: {comparison['タレントID一致率']['一致率']}")

        if comparison["詳細差異"]:
            print(f"\n【上位10名の差異】")
            for diff in comparison["詳細差異"]:
                print(f"  {diff['順位']}位:")
                print(f"    Phase A: {diff['Phase A']['名前']} (ID:{diff['Phase A']['ID']}, スコア:{diff['Phase A']['スコア']})")
                print(f"    Phase B: {diff['Phase B']['名前']} (ID:{diff['Phase B']['ID']}, スコア:{diff['Phase B']['スコア']})")

        # 結果をJSON出力
        output_file = f"/Users/lennon/projects/talent-casting-form/backend/verification_result_case{idx}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "test_case": test_case,
                "phase_a": {
                    "processing_time_ms": phase_a_time,
                    "results": phase_a_results[:5]  # 上位5名のみ
                },
                "phase_b": {
                    "processing_time_ms": phase_b_time,
                    "results": phase_b_results[:5]  # 上位5名のみ
                },
                "comparison": comparison
            }, f, ensure_ascii=False, indent=2)
        print(f"\n📄 詳細結果をファイルに出力: {output_file}")

    print("\n" + "=" * 80)
    print("検証完了")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
