#!/usr/bin/env python3
import requests
import json

def test_diagnosis():
    # 実際のユーザー条件でテスト
    payload = {
        "industry": "医薬品・医療・健康食品",
        "target_segments": "女性35-49歳",
        "purpose": "商品サービスの売上拡大",
        "budget": "1,000万円未満",
        "company_name": "株式会社テストクライアント",
        "email": "test@talent-casting-dev.local",
        "contact_name": "テスト太郎",
        "phone": "090-1234-5678",
        "genre_preference": "希望ジャンルあり",
        "preferred_genres": ["俳優", "アーティスト"]
    }

    response = requests.post(
        'http://localhost:8432/api/matching',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 200:
        data = response.json()

        print("=== 診断結果上位5名 ===")
        for i, talent in enumerate(data['results'][:5]):
            print(f"{talent['ranking']:2d}位: {talent['name']} | おすすめ: {talent['is_recommended']}")

        print(f"\n総結果数: {data['total_results']}")
        print(f"処理時間: {data['processing_time_ms']:.2f}ms")

        # おすすめタレントの詳細確認
        recommended_talents = [t for t in data['results'] if t['is_recommended']]
        print(f"\nおすすめタレント数: {len(recommended_talents)}")
        for talent in recommended_talents:
            print(f"  - {talent['ranking']}位: {talent['name']} (ID: {talent['account_id']})")

    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    test_diagnosis()