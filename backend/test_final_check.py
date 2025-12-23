#!/usr/bin/env python3
"""
最終確認: 本番環境で新垣結衣が除外され、他のタレントが正常に表示されることを確認
"""
import requests
import json

def test_final_production():
    """最終的な本番環境テスト"""
    base_url = "https://talent-casting-backend-fixed-392592761218.asia-northeast1.run.app"

    print("=" * 60)
    print("🎯 最終確認：修正版本番API動作テスト")
    print("=" * 60)

    test_data = {
        "industry": "ファッション",
        "target_segments": "女性20-34歳",
        "budget": "1,000万円～3,000万円未満",
        "purpose": "商品・サービスの特長訴求のため",
        "company_name": "テスト企業（修正版確認）",
        "email": "test@example.com",
        "phone": "03-1234-5678"
    }

    try:
        response = requests.post(
            f"{base_url}/api/matching",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        print(f"📊 レスポンスコード: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ マッチング成功!")

            # レスポンス構造の解析
            if 'results' in data:
                talents = data['results']
                talent_count = len(talents)

                print(f"📈 取得タレント数: {talent_count}名")
                print(f"📋 総結果数: {data.get('total_results', 'N/A')}")

                # 新垣結衣チェック
                aragaki_found = False
                sample_talents = []

                for i, talent in enumerate(talents):
                    name = talent.get('name', 'N/A')

                    if '新垣' in name:
                        aragaki_found = True
                        print(f"❌ 新垣結衣が見つかりました: {name}")
                        print(f"   account_id: {talent.get('account_id')}")
                        print(f"   matching_score: {talent.get('matching_score')}")

                    # サンプル表示
                    if i < 10:
                        score = talent.get('matching_score', 'N/A')
                        ranking = talent.get('ranking', 'N/A')
                        sample_talents.append(f"{ranking}位: {name} ({score}点)")

                # 結果判定
                if not aragaki_found:
                    print("✅ 新垣結衣は正しく除外されています")
                else:
                    print("❌ 新垣結衣が除外されていません")

                if talent_count > 0:
                    print("✅ 他のタレントが正しく表示されています")
                    print(f"\n📋 上位10名:")
                    for talent_info in sample_talents:
                        print(f"   {talent_info}")
                else:
                    print("❌ タレントが全く表示されていません")

                # 予算範囲の妥当性チェック
                budget_issues = []
                for talent in talents:
                    name = talent.get('name', 'N/A')
                    # 高額タレントかチェック（簡易版）
                    if '新垣' in name or '石原' in name or 'GACKT' in name:
                        budget_issues.append(name)

                if budget_issues:
                    print(f"⚠️ 高額タレントが表示されている可能性: {', '.join(budget_issues)}")
                else:
                    print("✅ 予算範囲の妥当性チェック: 問題なし")

            else:
                print("❌ レスポンス構造が不正です")
                print(f"   フィールド: {list(data.keys())}")

        else:
            print(f"❌ APIエラー: {response.status_code}")
            print(f"   エラーレスポンス: {response.text[:500]}")

    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")

    print("\n" + "=" * 60)
    print("🏁 テスト完了")
    print("=" * 60)

if __name__ == "__main__":
    test_final_production()