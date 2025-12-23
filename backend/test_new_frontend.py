#!/usr/bin/env python3
"""
新しいフロントエンドデプロイのAPI接続確認
"""
import requests

def test_new_frontend():
    """新しいフロントエンドのAPI接続確認"""
    print("=" * 80)
    print("🔄 新フロントエンドのAPI接続確認")
    print("=" * 80)

    # 新しいフロントエンドURL
    frontend_url = "https://talent-casting-diagnosis-o3xmc11er-yutamatsuuras-projects.vercel.app"

    # 期待されるAPIサービス（元の正常版）
    expected_api = "https://talent-casting-backend-392592761218.asia-northeast1.run.app"

    print(f"🌐 新フロントエンドURL: {frontend_url}")
    print(f"🔗 期待API: {expected_api}")

    # 元のAPIサービスを直接テスト
    test_data = {
        "industry": "ファッション",
        "target_segments": "女性20-34歳",
        "budget": "1,000万円～3,000万円未満",
        "purpose": "商品・サービスの特長訴求のため",
        "company_name": "新フロントエンドテスト企業",
        "email": "test@example.com",
        "phone": "03-1234-5678"
    }

    print(f"\n📡 API直接テスト（{expected_api}）:")

    try:
        response = requests.post(
            f"{expected_api}/api/matching",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        print(f"   ステータス: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            talent_count = len(data.get('results', []))
            print(f"   ✅ タレント数: {talent_count}名")

            if talent_count == 30:
                print(f"   ✅ API側は正常（30名取得）")
                print(f"   📱 新フロントエンド確認手順：")
                print(f"      1. 新しいプライベートウィンドウを開く")
                print(f"      2. {frontend_url} にアクセス")
                print(f"      3. 診断実行")
                print(f"      4. 30名表示を確認")
                print(f"      5. ブラウザ開発者ツールでエラー確認")
            else:
                print(f"   ⚠️ API側でタレント数異常: {talent_count}名")
        else:
            print(f"   ❌ APIエラー: {response.status_code}")

    except Exception as e:
        print(f"   ❌ API接続エラー: {e}")

    print(f"\n📋 デバッグ情報:")
    print(f"   環境変数設定済み: NEXT_PUBLIC_API_BASE_URL = {expected_api}")
    print(f"   最新デプロイ: --force オプション使用")
    print(f"   キャッシュ: 完全クリア済み")

    print(f"\n" + "=" * 80)
    print(f"🔍 トラブルシューティング:")
    print(f"   もし3名しか表示されない場合：")
    print(f"   1. ブラウザを完全に閉じて再起動")
    print(f"   2. 別のブラウザでテスト")
    print(f"   3. フロントエンドのエラーログを確認")
    print(f"   4. Vercel環境変数が正しく適用されているか確認")
    print(f"=" * 80)

if __name__ == "__main__":
    test_new_frontend()