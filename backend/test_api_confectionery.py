#!/usr/bin/env python3
"""菓子・氷菓業界API直接テスト"""
import asyncio
import aiohttp
import json

async def test_matching_api():
    """マッチングAPIを直接テスト"""

    # テストデータ（スクリーンショットと同じ条件）
    test_data = {
        "industry": "菓子・氷菓",
        "target_segments": "女性20-34歳",
        "purpose": "商品サービスの売上拡大",
        "budget": "1,000万円未満",
        "company_name": "株式会社テストクライアント",
        "email": "test@talent-casting-dev.local",
        "contact_name": "テスト太郎",
        "phone": "090-1234-5678",
        "genre_preference": "希望ジャンルあり",
        "preferred_genres": ["俳優", "アーティスト"]
    }

    print("=== マッチングAPI直接テスト ===")
    print(f"テスト条件:")
    print(f"  業界: {test_data['industry']}")
    print(f"  ターゲット: {test_data['target_segments']}")
    print(f"  予算: {test_data['budget']}")
    print()

    try:
        async with aiohttp.ClientSession() as session:
            # ローカルAPIエンドポイントにPOST
            async with session.post(
                'http://localhost:8432/api/matching',
                json=test_data,
                headers={'Content-Type': 'application/json'}
            ) as response:

                print(f"レスポンスステータス: {response.status}")

                if response.status == 200:
                    data = await response.json()

                    print(f"成功: {data.get('success', False)}")
                    print(f"結果件数: {data.get('total_results', 0)}")
                    print(f"処理時間: {data.get('processing_time_ms', 0)}ms")
                    print()

                    results = data.get('results', [])
                    if results:
                        print("=== 上位10名の競合利用中状況 ===")
                        for i, talent in enumerate(results[:10], 1):
                            is_in_cm = talent.get('is_currently_in_cm', False)
                            cm_status = "競合利用中" if is_in_cm else "利用可能"
                            name = talent.get('name', '不明')
                            score = talent.get('matching_score', 0)
                            print(f"{i:2d}. {name:<12} | {score:5.1f} | {cm_status}")

                        print()

                        # 競合利用中のタレント数をカウント
                        cm_count = sum(1 for t in results if t.get('is_currently_in_cm', False))
                        print(f"競合利用中タレント数: {cm_count}/{len(results)}")

                        # 競合利用中のタレントリスト
                        if cm_count > 0:
                            print("\n=== 競合利用中タレント詳細 ===")
                            cm_talents = [t for t in results if t.get('is_currently_in_cm', False)]
                            for talent in cm_talents:
                                print(f"- {talent.get('name', '不明')} (ID: {talent.get('account_id', '不明')})")
                        else:
                            print("\n⚠️  競合利用中のタレントが0人です")

                        # レスポンス構造の詳細確認
                        print(f"\n=== 1番目のタレント詳細 ===")
                        first = results[0]
                        for key, value in first.items():
                            print(f"  {key}: {value}")

                    else:
                        print("❌ 結果が空です")
                else:
                    error_text = await response.text()
                    print(f"❌ エラーレスポンス: {error_text}")

    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        print("バックエンドが起動していることを確認してください")

if __name__ == "__main__":
    asyncio.run(test_matching_api())