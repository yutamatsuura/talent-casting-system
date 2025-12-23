#!/usr/bin/env python3
"""
CSV出力での予算フィルター問題を調査
1000万円未満 vs 1億円以上での結果比較
"""
import asyncio
import asyncpg
from app.services.enhanced_matching_debug import EnhancedMatchingDebug

async def test_budget_filter_difference():
    """予算条件による結果の違いをテスト"""
    print("=" * 80)
    print("🔍 予算フィルター問題調査 - CSV出力用ロジック")
    print("=" * 80)

    # テスト条件
    industry = "ファッション"
    target_segments = ["女性20-34歳"]
    purpose = "商品サービスの特長訴求のため"

    # 予算条件1: 1000万円未満
    budget_1 = "1,000万円未満"

    # 予算条件2: 1億円以上
    budget_2 = "1億円以上"

    debug_matcher = EnhancedMatchingDebug()

    print(f"📊 テスト条件:")
    print(f"   業界: {industry}")
    print(f"   ターゲット: {target_segments[0]}")
    print(f"   目的: {purpose}")

    try:
        print(f"\n🧪 テスト1: 予算 = {budget_1}")
        results_1 = await debug_matcher.generate_complete_talent_analysis(
            industry=industry,
            target_segments=target_segments,
            purpose=purpose,
            budget=budget_1
        )
        print(f"   結果数: {len(results_1)} 件")
        if len(results_1) > 0:
            print(f"   1位: {results_1[0].get('タレント名', 'N/A')}")
        else:
            print(f"   ❌ 結果なし")

        print(f"\n🧪 テスト2: 予算 = {budget_2}")
        results_2 = await debug_matcher.generate_complete_talent_analysis(
            industry=industry,
            target_segments=target_segments,
            purpose=purpose,
            budget=budget_2
        )
        print(f"   結果数: {len(results_2)} 件")
        if len(results_2) > 0:
            print(f"   1位: {results_2[0].get('タレント名', 'N/A')}")
        else:
            print(f"   ❌ 結果なし")

        # 詳細比較
        print(f"\n📋 比較結果:")
        print(f"   1000万円未満: {len(results_1)} 件")
        print(f"   1億円以上:   {len(results_2)} 件")

        if len(results_1) == 0 and len(results_2) > 0:
            print(f"   🚨 問題確認: 1000万円未満で結果が0件になっている")
        elif len(results_1) > 0 and len(results_2) > 0:
            print(f"   ✅ 両方で結果が取得できている")

    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_budget_filter_difference())