#!/usr/bin/env python3
"""
年間最低・最高金額追加版のCSV出力テスト
"""
import asyncio
from app.api.endpoints.matching import execute_matching_logic, get_matching_parameters, apply_recommended_talents_integration
from app.schemas.matching import MatchingFormData
from app.api.endpoints.admin import convert_matching_results_to_csv_format

async def test_csv_with_money_columns():
    """年間金額追加版のCSV出力テスト"""
    print("=" * 80)
    print("🔍 年間金額追加版CSV出力テスト")
    print("=" * 80)

    # テスト条件（1000万円未満）
    form_data = MatchingFormData(
        industry="ファッション",
        target_segments="女性20-34歳",
        purpose="商品サービスの特長訴求のため",
        budget="1,000万円未満",
        company_name="テスト",
        email="test@example.com",
        contact_name="テスト太郎",
        phone="090-1234-5678",
        session_id="test-session"
    )

    try:
        print("🔧 マッチングパラメータ取得中...")
        max_budget, target_segment_id, image_item_ids = await get_matching_parameters(
            form_data.budget, form_data.target_segments, form_data.industry
        )

        print("⚡ execute_matching_logic実行中...")
        raw_results = await execute_matching_logic(
            form_data, max_budget, target_segment_id, image_item_ids
        )

        print("🔗 おすすめタレント統合中...")
        integrated_results = await apply_recommended_talents_integration(
            form_data, raw_results
        )

        print("📋 18列CSV形式変換中...")
        detailed_results = await convert_matching_results_to_csv_format(
            integrated_results, "ファッション", "女性20-34歳"
        )

        print(f"✅ 結果: {len(detailed_results)}件")
        if len(detailed_results) > 0:
            first_talent = detailed_results[0]
            print(f"   1位タレント: {first_talent['タレント名']}")
            print(f"   年間最低金額: {first_talent['年間最低金額']}")
            print(f"   年間最高金額: {first_talent['年間最高金額']}")
            print(f"   総列数: {len(first_talent)}列")

            print(f"\n📋 新しいCSV列順:")
            for i, column_name in enumerate(first_talent.keys(), 1):
                print(f"   {i:2d}. {column_name}")
        else:
            print("   ❌ 結果が0件です")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_csv_with_money_columns())