#!/usr/bin/env python3
"""
CSV出力API直接テスト - ローカルでの詳細デバッグ
"""
import asyncio
import asyncpg
from app.api.endpoints.matching import execute_matching_logic, get_matching_parameters
from app.schemas.matching import MatchingFormData

async def test_csv_logic_directly():
    """CSV出力ロジックを直接テスト"""
    print("=" * 80)
    print("🔍 CSV出力ロジック直接テスト")
    print("=" * 80)

    # 問題の条件を再現
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
        print(f"📊 テスト条件:")
        print(f"   業界: {form_data.industry}")
        print(f"   ターゲット: {form_data.target_segments}")
        print(f"   目的: {form_data.purpose}")
        print(f"   予算: {form_data.budget}")

        # マッチングパラメータ取得
        print(f"\n🔧 マッチングパラメータ取得中...")
        max_budget, target_segment_id, image_item_ids = await get_matching_parameters(
            form_data.budget, form_data.target_segments, form_data.industry
        )
        print(f"   max_budget: {max_budget}")
        print(f"   target_segment_id: {target_segment_id}")
        print(f"   image_item_ids: {image_item_ids}")

        # execute_matching_logic実行
        print(f"\n⚡ execute_matching_logic実行中...")
        raw_results = await execute_matching_logic(
            form_data, max_budget, target_segment_id, image_item_ids
        )
        print(f"   raw_results件数: {len(raw_results)}")

        if len(raw_results) > 0:
            print(f"   1位: {raw_results[0].get('name', 'N/A')}")
        else:
            print(f"   ❌ 結果が0件です")

        # おすすめタレント統合も確認
        from app.api.endpoints.matching import apply_recommended_talents_integration
        print(f"\n🔗 おすすめタレント統合実行中...")
        integrated_results = await apply_recommended_talents_integration(
            form_data, raw_results
        )
        print(f"   integrated_results件数: {len(integrated_results)}")

        if len(integrated_results) > 0:
            print(f"   1位: {integrated_results[0].get('name', 'N/A')}")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_csv_logic_directly())