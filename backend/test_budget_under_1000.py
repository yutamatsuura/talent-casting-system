#!/usr/bin/env python3
"""
1,000万円未満の予算範囲テストスクリプト
"""
import requests
import json

def test_budget_ranges():
    """様々な予算範囲でマッチングテストを実行"""

    # テスト用の基本データ
    base_data = {
        "industry": "化粧品・ヘアケア・オーラルケア",
        "target_segments": ["女性20-34歳"],
        "company_name": "テスト株式会社",
        "email": "test@talent-casting-dev.local"
    }

    # テストする予算範囲（実際に存在する範囲のみ）
    budget_ranges = [
        "1,000万円未満",
        "1,000万円～3,000万円未満",
        "3,000万円～1億円未満"
    ]

    print("=== 予算範囲別マッチングテスト ===")
    print()

    for budget in budget_ranges:
        print(f"🎯 予算範囲: {budget}")

        # リクエストデータ作成
        test_data = base_data.copy()
        test_data["budget"] = budget

        try:
            # APIリクエスト
            response = requests.post(
                "http://localhost:8432/api/matching",
                json=test_data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                filtered_count = result.get("summary", {}).get("filtered_talents_count", 0)
                total_results = len(result.get("results", []))

                print(f"  ✅ フィルタ後タレント数: {filtered_count}人")
                print(f"  📊 マッチング結果数: {total_results}人")

                # 結果のサンプル表示
                if result.get("results"):
                    top3 = result["results"][:3]
                    print("  📋 トップ3:")
                    for i, talent in enumerate(top3, 1):
                        name = talent.get("name", "不明")
                        score = talent.get("matching_score", 0)
                        rank = talent.get("rank", i)
                        print(f"    {rank}位: {name} (スコア: {score})")

            else:
                print(f"  ❌ エラー: {response.status_code}")
                print(f"  詳細: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"  ❌ リクエストエラー: {e}")

        print()

if __name__ == "__main__":
    test_budget_ranges()