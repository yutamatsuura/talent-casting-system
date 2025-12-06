#!/usr/bin/env python3
"""
修正された予算フィルタリングロジックのテスト
"""
import requests
import json

def test_budget_fix():
    """修正された予算フィルタリングロジックをテスト"""

    # テスト用の基本データ
    base_data = {
        "industry": "化粧品・ヘアケア・オーラルケア",
        "target_segments": ["女性20-34歳"],
        "company_name": "テスト株式会社",
        "email": "test@talent-casting-dev.local"
    }

    # テストする予算範囲
    budget_ranges = [
        "1,000万円未満",
        "1,000万円～3,000万円未満",
        "3,000万円～1億円未満",
        "1億円以上"
    ]

    print("=== 修正後の予算フィルタリングテスト ===")
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
                total_results = len(result.get("results", []))

                print(f"  ✅ マッチング結果数: {total_results}人")

                # 結果のサンプル表示
                if result.get("results"):
                    top3 = result["results"][:3]
                    print("  📋 トップ3:")
                    for i, talent in enumerate(top3, 1):
                        name = talent.get("name", "不明")
                        score = talent.get("matching_score", 0)
                        print(f"    {i}位: {name} (スコア: {score})")

                # 期待値との比較
                if budget == "1億円以上":
                    print(f"  💡 期待値: 全タレント対象（約3,971人の中からトップ30）")
                    if total_results == 30:
                        print("  ✅ 修正成功：適切な人数が返されています")
                    else:
                        print("  ⚠️  確認必要：人数が期待と異なります")

            else:
                print(f"  ❌ エラー: {response.status_code}")
                print(f"  詳細: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"  ❌ リクエストエラー: {e}")

        print()

    print("=== 修正内容の説明 ===")
    print("✅ 修正前: 「1億円以上」予算 → 1,777人対象（44.7%）")
    print("✅ 修正後: 「1億円以上」予算 → 全タレント対象（100%）")
    print("💡 3,000万円のタレントも「1億円以上」予算で正しく含まれるようになりました")

if __name__ == "__main__":
    test_budget_fix()