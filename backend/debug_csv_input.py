#!/usr/bin/env python3
"""
convert_matching_results_to_csv_formatへの入力データを確認
"""
import asyncio
from app.api.endpoints.matching import execute_matching_logic, get_matching_parameters, apply_recommended_talents_integration
from app.schemas.matching import MatchingFormData

async def debug_csv_input():
    """CSV形式変換への入力データをデバッグ"""
    print("=" * 80)
    print("🔍 CSV入力データデバッグ")
    print("=" * 80)

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
        print("🔧 ステップ1: パラメータ取得")
        max_budget, target_segment_id, image_item_ids = await get_matching_parameters(
            form_data.budget, form_data.target_segments, form_data.industry
        )

        print("⚡ ステップ2: execute_matching_logic")
        raw_results = await execute_matching_logic(
            form_data, max_budget, target_segment_id, image_item_ids
        )
        print(f"   raw_results: {len(raw_results)}件")

        print("🔗 ステップ3: おすすめタレント統合")
        integrated_results = await apply_recommended_talents_integration(
            form_data, raw_results
        )
        print(f"   integrated_results: {len(integrated_results)}件")

        if len(integrated_results) > 0:
            print("\n📊 integrated_resultsサンプル:")
            for i, talent in enumerate(integrated_results[:3]):
                print(f"   {i+1}. account_id: {talent.get('account_id')}, name: {talent.get('name')}, ranking: {talent.get('ranking')}")

        # これが convert_matching_results_to_csv_format への入力になる
        print(f"\n🎯 convert_matching_results_to_csv_formatの入力:")
        print(f"   matching_results: {len(integrated_results)}件")
        print(f"   industry: ファッション")
        print(f"   target_segment: 女性20-34歳")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_csv_input())