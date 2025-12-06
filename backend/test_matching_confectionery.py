#!/usr/bin/env python3
"""菓子・氷菓業界での競合利用中ラベル表示テスト"""
import asyncio
import json
from app.api.endpoints.matching import execute_matching
from app.schemas.matching import MatchingFormData

async def test_confectionery_matching():
    """菓子・氷菓業界でのマッチングテスト"""

    # テストフォームデータ（スクリーンショットと同じ条件）
    form_data = MatchingFormData(
        industry="菓子・氷菓",
        target_segments="女性20-34歳",
        purpose="商品サービスの売上拡大",
        budget="1,000万円未満",
        company_name="株式会社テストクライアント",
        email="test@talent-casting-dev.local",
        contact_name="テスト太郎",
        phone="090-1234-5678",
        genre_preference="希望ジャンルあり",
        preferred_genres=["俳優", "アーティスト"]
    )

    print("=== 菓子・氷菓業界マッチングテスト ===")
    print(f"業界: {form_data.industry}")
    print(f"ターゲット: {form_data.target_segments}")
    print(f"予算: {form_data.budget}")
    print()

    try:
        # マッチング実行
        response = await execute_matching(form_data)

        print(f"結果件数: {response.total_results}")
        print(f"処理時間: {response.processing_time_ms}ms")
        print()

        # 上位10名を確認
        print("=== 上位10名の競合利用中状況 ===")
        for i, talent in enumerate(response.results[:10], 1):
            cm_status = "競合利用中" if talent.is_currently_in_cm else "利用可能"
            print(f"{i:2d}. {talent.name:<10} | {talent.matching_score:5.1f} | {cm_status}")

        print()

        # 競合利用中のタレント数をカウント
        cm_count = sum(1 for t in response.results if t.is_currently_in_cm)
        print(f"競合利用中タレント数: {cm_count}/{len(response.results)}")

        # 競合利用中のタレントリスト
        if cm_count > 0:
            print("\n=== 競合利用中タレント一覧 ===")
            cm_talents = [t for t in response.results if t.is_currently_in_cm]
            for talent in cm_talents:
                print(f"- {talent.name} (account_id: {talent.account_id})")
        else:
            print("\n⚠️  競合利用中のタレントが0人です")

        # レスポンス構造を詳細確認
        print(f"\n=== レスポンス構造確認 ===")
        if response.results:
            first_talent = response.results[0]
            print(f"サンプルタレント: {first_talent.name}")
            print(f"  - account_id: {first_talent.account_id}")
            print(f"  - is_currently_in_cm: {first_talent.is_currently_in_cm}")
            print(f"  - matching_score: {first_talent.matching_score}")
            print(f"  - ranking: {first_talent.ranking}")

        return response

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_confectionery_matching())