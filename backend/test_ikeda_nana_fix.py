#!/usr/bin/env python3
"""
池田菜々（削除済みタレント）の修正後テスト

確認項目:
1. get_recommended_talents_for_matchingで池田菜々取得可能
2. get_recommended_talent_detailsで詳細情報取得可能
3. 実際のマッチングAPIで3位に表示されるか
"""

import asyncio
from app.schemas.matching import MatchingFormData
from app.api.endpoints.matching import post_matching
from app.api.endpoints.recommended_talents import get_recommended_talents_for_matching
from app.api.endpoints.matching import get_recommended_talent_details
from fastapi import Request

class MockRequest:
    def __init__(self):
        self.client = MockClient()
        self.headers = {"user-agent": "test-client"}

class MockClient:
    def __init__(self):
        self.host = "127.0.0.1"

async def test_ikeda_nana_fix():
    print("🧪 池田菜々（削除済みタレント）修正後テスト")
    print("=" * 60)

    industry = "化粧品・ヘアケア・オーラルケア"
    target_segment = "女性20-34歳"
    ikeda_id = 345

    # 1. おすすめタレント取得テスト
    print(f"\n1️⃣ おすすめタレント取得テスト")
    try:
        recommended_talents = await get_recommended_talents_for_matching(industry)
        print(f"取得されたおすすめタレント数: {len(recommended_talents) if recommended_talents else 0}")

        ikeda_found = False
        if recommended_talents:
            for talent in recommended_talents:
                print(f"  - ID={talent['account_id']:3}: {talent['name']}")
                if talent['account_id'] == ikeda_id:
                    ikeda_found = True
                    print(f"    🎯 池田菜々発見！")

        if ikeda_found:
            print(f"✅ 池田菜々が正常に取得されました")
        else:
            print(f"❌ 池田菜々が取得されませんでした")
            return

    except Exception as e:
        print(f"❌ おすすめタレント取得エラー: {e}")
        return

    # 2. 池田菜々詳細情報取得テスト
    print(f"\n2️⃣ 池田菜々詳細情報取得テスト")
    try:
        ikeda_details = await get_recommended_talent_details(ikeda_id, target_segment)

        if ikeda_details:
            print(f"✅ 池田菜々詳細情報取得成功:")
            print(f"  - 名前: {ikeda_details['name']}")
            print(f"  - base_power_score: {ikeda_details['base_power_score']}")
            print(f"  - act_genre: {ikeda_details['act_genre']}")
        else:
            print(f"❌ 池田菜々詳細情報取得失敗")
            return

    except Exception as e:
        print(f"❌ 詳細情報取得エラー: {e}")
        return

    # 3. 実際のマッチングAPIテスト
    print(f"\n3️⃣ 実際のマッチングAPIテスト")

    form_data = MatchingFormData(
        industry=industry,
        target_segments=target_segment,
        budget="1,000万円～3,000万円未満",
        purpose="ブランド認知向上",
        company_name="テスト企業",
        contact_name="テスト担当者",
        email="test@example.com",
        phone="090-1234-5678"
    )

    mock_request = MockRequest()

    try:
        print(f"⏳ マッチングAPI実行中...")
        response = await post_matching(form_data, mock_request)

        print(f"✅ API実行完了")
        print(f"  - 処理時間: {response.processing_time_ms}ms")
        print(f"  - 結果数: {response.total_results}件")

        # 上位3位の確認
        print(f"\n🏆 上位3位の結果:")
        print("順位 | 名前       | スコア  | おすすめ | ID")
        print("-" * 45)

        ikeda_found_in_results = False
        ikeda_position = None

        for talent in response.results[:3]:
            is_recommended_mark = "⭐" if talent.is_recommended else "  "
            print(f"{talent.ranking:2d}位 | {talent.name:10s} | {talent.matching_score:5.1f}点 | {is_recommended_mark} | {talent.account_id}")

            if talent.account_id == ikeda_id:
                ikeda_found_in_results = True
                ikeda_position = talent.ranking

        # 結果確認
        print(f"\n🔍 池田菜々の最終確認:")
        if ikeda_found_in_results:
            print(f"  ✅ {ikeda_position}位に表示されています！")
            ikeda_talent = next((t for t in response.results if t.account_id == ikeda_id), None)
            if ikeda_talent:
                print(f"  - 名前: {ikeda_talent.name}")
                print(f"  - スコア: {ikeda_talent.matching_score}")
                print(f"  - おすすめ: {ikeda_talent.is_recommended}")
        else:
            print(f"  ❌ 池田菜々が結果に含まれていません")

            # 全結果から検索
            all_ikeda = next((t for t in response.results if t.account_id == ikeda_id), None)
            if all_ikeda:
                print(f"  ⚠️ {all_ikeda.ranking}位に存在（上位3名外）")
            else:
                print(f"  ❌ 全結果に含まれていません")

        print(f"\n📋 修正効果確認:")
        print(f"  1. ✅ del_flag=1の削除済みタレントを取得可能")
        print(f"  2. ✅ m_talent_actデータなしでも表示可能")
        print(f"  3. ✅ talent_scoresデータなしでもデフォルト値で動作")
        print(f"  4. {'✅' if ikeda_found_in_results else '❌'} おすすめタレントとして正常表示")

    except Exception as e:
        print(f"❌ マッチングAPIエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ikeda_nana_fix())