#!/usr/bin/env python3
"""
EnhancedMatchingDebugとexecute_matching_logic+integrationの
データ形式比較
"""
import asyncio
import asyncpg
from app.api.endpoints.matching import execute_matching_logic, get_matching_parameters, apply_recommended_talents_integration
from app.schemas.matching import MatchingFormData
from app.services.enhanced_matching_debug import EnhancedMatchingDebug

async def compare_data_formats():
    """データ形式の詳細比較"""
    print("=" * 80)
    print("🔍 データ形式比較テスト")
    print("=" * 80)

    # テスト条件
    industry = "ファッション"
    target_segments = ["女性20-34歳"]
    purpose = "商品サービスの特長訴求のため"
    budget = "1,000万円未満"

    form_data = MatchingFormData(
        industry=industry,
        target_segments=target_segments[0],
        purpose=purpose,
        budget=budget,
        company_name="テスト",
        email="test@example.com"
    )

    try:
        print("🧪 テスト1: EnhancedMatchingDebug")
        debug_matcher = EnhancedMatchingDebug()
        enhanced_results = await debug_matcher.generate_complete_talent_analysis(
            industry=industry,
            target_segments=target_segments,
            purpose=purpose,
            budget=budget
        )
        print(f"   結果数: {len(enhanced_results)}")
        if len(enhanced_results) > 0:
            print(f"   1位データ構造:")
            first_result = enhanced_results[0]
            for key in sorted(first_result.keys()):
                print(f"     {key}: {type(first_result[key])}")

        print(f"\n🧪 テスト2: execute_matching_logic + integration")
        max_budget, target_segment_id, image_item_ids = await get_matching_parameters(
            form_data.budget, form_data.target_segments, form_data.industry
        )

        raw_results = await execute_matching_logic(
            form_data, max_budget, target_segment_id, image_item_ids
        )

        integrated_results = await apply_recommended_talents_integration(
            form_data, raw_results
        )

        print(f"   結果数: {len(integrated_results)}")
        if len(integrated_results) > 0:
            print(f"   1位データ構造:")
            first_result = integrated_results[0]
            for key in sorted(first_result.keys()):
                print(f"     {key}: {type(first_result[key])}")

        # キーの差分確認
        if len(enhanced_results) > 0 and len(integrated_results) > 0:
            enhanced_keys = set(enhanced_results[0].keys())
            integrated_keys = set(integrated_results[0].keys())

            print(f"\n📋 キー差分:")
            print(f"   enhanced_onlyキー: {enhanced_keys - integrated_keys}")
            print(f"   integrated_onlyキー: {integrated_keys - enhanced_keys}")
            print(f"   共通キー数: {len(enhanced_keys & integrated_keys)}")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(compare_data_formats())