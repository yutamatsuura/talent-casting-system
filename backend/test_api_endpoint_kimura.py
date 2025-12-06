#!/usr/bin/env python3
"""
実際のマッチングAPIエンドポイントで仁村紗和の表示を確認

テスト項目:
1. 化粧品業界での実際のAPIレスポンス
2. 仁村紗和が1位に表示されるかの確認
3. 全30名の結果を詳細に確認
"""

import asyncio
import json
from app.schemas.matching import MatchingFormData
from app.api.endpoints.matching import post_matching
from fastapi import Request

class MockRequest:
    """テスト用のMockRequestクラス"""
    def __init__(self):
        self.client = MockClient()
        self.headers = {"user-agent": "test-client"}

class MockClient:
    def __init__(self):
        self.host = "127.0.0.1"

async def test_api_endpoint_kimura():
    print("🧪 実際のマッチングAPIエンドポイントテスト")
    print("=" * 60)

    # テストデータ作成
    form_data = MatchingFormData(
        industry="化粧品・ヘアケア・オーラルケア",
        target_segments="女性20-34歳",
        budget="1,000万円～3,000万円未満",
        purpose="ブランド認知向上",
        company_name="テスト企業",
        contact_name="テスト担当者",
        email="test@example.com",
        phone="090-1234-5678"
    )

    mock_request = MockRequest()

    try:
        print(f"📋 テスト条件:")
        print(f"  - 業種: {form_data.industry}")
        print(f"  - ターゲット: {form_data.target_segments}")
        print(f"  - 予算: {form_data.budget}")

        # 実際のAPIエンドポイント実行
        print(f"\n⏳ マッチングAPI実行中...")
        response = await post_matching(form_data, mock_request)

        print(f"✅ API実行完了")
        print(f"  - 処理時間: {response.processing_time_ms}ms")
        print(f"  - 結果数: {response.total_results}件")
        print(f"  - 成功: {response.success}")

        # 上位10名の詳細確認
        print(f"\n🏆 上位10名の結果:")
        print("順位 | 名前           | スコア  | おすすめ | ID")
        print("-" * 50)

        kimura_found = False
        kimura_position = None

        for i, talent in enumerate(response.results[:10]):
            is_recommended_mark = "⭐" if talent.is_recommended else "  "
            print(f"{talent.ranking:2d}位 | {talent.name:12s} | {talent.matching_score:5.1f}点 | {is_recommended_mark} | {talent.account_id}")

            if talent.account_id == 123:  # 仁村紗和のID
                kimura_found = True
                kimura_position = talent.ranking

        # 仁村紗和の確認
        print(f"\n🔍 仁村紗和の結果確認:")
        if kimura_found:
            print(f"  ✅ {kimura_position}位に表示されています")
            kimura_talent = next((t for t in response.results if t.account_id == 123), None)
            if kimura_talent:
                print(f"  - 名前: {kimura_talent.name}")
                print(f"  - スコア: {kimura_talent.matching_score}")
                print(f"  - おすすめ: {kimura_talent.is_recommended}")
                print(f"  - base_power_score: {kimura_talent.base_power_score}")
                print(f"  - image_adjustment: {kimura_talent.image_adjustment}")
        else:
            print(f"  ❌ 仁村紗和が結果に含まれていません")

            # 全結果から仁村紗和を検索
            all_talents = response.results
            kimura_in_all = next((t for t in all_talents if t.account_id == 123), None)

            if kimura_in_all:
                print(f"  ⚠️ {kimura_in_all.ranking}位に存在（上位10名外）")
                print(f"      スコア: {kimura_in_all.matching_score}")
                print(f"      おすすめ: {kimura_in_all.is_recommended}")
            else:
                print(f"  ❌ 全30名の結果に含まれていません")

        # おすすめタレント確認
        recommended_talents = [t for t in response.results[:3] if t.is_recommended]
        print(f"\n⭐ おすすめタレント確認（1-3位）:")
        for talent in recommended_talents:
            mark = "🎯" if talent.account_id == 123 else "  "
            print(f"  {mark} {talent.ranking}位: {talent.name} (ID: {talent.account_id})")

    except Exception as e:
        print(f"❌ APIテストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api_endpoint_kimura())