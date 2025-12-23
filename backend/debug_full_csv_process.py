#!/usr/bin/env python3
"""
CSV出力プロセス全体をローカルでテスト
"""
import asyncio
from app.api.endpoints.matching import execute_matching_logic, get_matching_parameters, apply_recommended_talents_integration
from app.schemas.matching import MatchingFormData
from convert_to_csv_format import convert_matching_results_to_csv_format

async def test_full_csv_process():
    """CSV出力プロセス全体をテスト"""
    print("=" * 80)
    print("🔍 CSV出力プロセス全体テスト")
    print("=" * 80)

    # 送信ID 411の実際のデータを模擬
    form_data = MatchingFormData(
        industry="ファッション",
        target_segments="女性20-34歳",
        purpose="商品サービスの特長訴求のため",
        budget="1,000万円未満",
        company_name="テスト",
        email="test@example.com",
        contact_name="テスト太郎",
        phone="090-1234-5678",
        session_id="3ccbef79-9fb6-40d2-a071-6296b220abc6"
    )

    try:
        print("🔧 ステップ1: マッチングパラメータ取得")
        max_budget, target_segment_id, image_item_ids = await get_matching_parameters(
            form_data.budget, form_data.target_segments, form_data.industry
        )
        print(f"   max_budget: {max_budget}")
        print(f"   target_segment_id: {target_segment_id}")
        print(f"   image_item_ids: {image_item_ids}")

        print(f"\n⚡ ステップ2: execute_matching_logic")
        raw_results = await execute_matching_logic(
            form_data, max_budget, target_segment_id, image_item_ids
        )
        print(f"   raw_results: {len(raw_results)}件")

        print(f"\n🔗 ステップ3: おすすめタレント統合")
        integrated_results = await apply_recommended_talents_integration(
            form_data, raw_results
        )
        print(f"   integrated_results: {len(integrated_results)}件")

        print(f"\n📋 ステップ4: CSV形式変換")
        detailed_results = await convert_matching_results_to_csv_format(
            integrated_results, "ファッション", "女性20-34歳"
        )
        print(f"   detailed_results: {len(detailed_results)}件")

        if len(detailed_results) > 0:
            print(f"   1位: {detailed_results[0]['タレント名']}")
            print(f"   CSV列数: {len(detailed_results[0])}列")
            print(f"   列名: {list(detailed_results[0].keys())}")
        else:
            print(f"   ❌ CSV変換結果が0件")

    except Exception as e:
        print(f"❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_csv_process())