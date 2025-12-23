#!/usr/bin/env python3
"""
本番環境の修正版API（talent-casting-backend-fixed）で動作確認
新垣結衣が除外され、他のタレントが表示されることを確認
"""
import requests
import json

def test_production_api():
    """本番環境のAPIをテスト"""
    base_url = "https://talent-casting-backend-fixed-392592761218.asia-northeast1.run.app"

    print("=" * 60)
    print("本番環境API動作確認（修正版）")
    print("=" * 60)

    # テストデータ（新垣結衣が除外されるべき条件）
    test_data = {
        "industry": "ファッション",
        "target_segments": "女性20-34歳",
        "budget": "1,000万円～3,000万円未満",
        "purpose": "商品・サービスの特長訴求のため",
        "company_name": "テスト企業（修正版確認）",
        "email": "test@example.com",
        "phone": "03-1234-5678"
    }

    print(f"APIエンドポイント: {base_url}/api/matching")
    print(f"テストデータ:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    print()

    try:
        # マッチングAPIを呼び出し
        response = requests.post(
            f"{base_url}/api/matching",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        print(f"レスポンスコード: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # 結果の検証
            if 'talents' in data and isinstance(data['talents'], list):
                talents = data['talents']
                talent_count = len(talents)

                print(f"✅ マッチング成功!")
                print(f"   取得タレント数: {talent_count}名")

                # 新垣結衣がいるかチェック
                aragaki_found = False
                sample_talents = []

                for i, talent in enumerate(talents):
                    if 'name' in talent:
                        name = talent['name']
                        if '新垣' in name:
                            aragaki_found = True
                            print(f"❌ 新垣結衣が見つかりました: {name}")

                        # サンプル表示（上位5名）
                        if i < 5:
                            score = talent.get('matching_score', 'N/A')
                            sample_talents.append(f"{name} ({score}点)")

                if not aragaki_found:
                    print("✅ 新垣結衣は正しく除外されています")

                if talent_count > 0:
                    print("✅ 他のタレントが正しく表示されています")
                    print(f"   上位5名: {', '.join(sample_talents[:5])}")
                else:
                    print("❌ タレントが全く表示されていません")

            else:
                print("❌ レスポンス形式が不正です")
                print(f"   レスポンス: {response.text[:500]}")

        else:
            print(f"❌ APIエラー: {response.status_code}")
            print(f"   レスポンス: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")

if __name__ == "__main__":
    test_production_api()