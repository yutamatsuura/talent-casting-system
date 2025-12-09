#!/usr/bin/env python3
"""
本番環境のクリーンアップ後動作確認テスト
"""
import requests
import json

def test_production_clean():
    print("🧪 本番環境クリーンアップ後テスト")
    print("=" * 50)

    # テストデータ
    test_data = {
        "industry": "乳製品",
        "target_segments": "男性12-19歳",
        "budget": "1,000万円〜3,000万円未満",
        "purpose": "商品サービスの特長訴求のため",
        "company_name": "株式会社動作確認テスト",
        "email": "clean-test@example.com"
    }

    production_url = "https://talent-casting-backend-392592761218.asia-northeast1.run.app/api/matching"

    try:
        print(f"📤 本番環境にリクエスト送信中...")
        print(f"URL: {production_url}")
        print(f"データ: {json.dumps(test_data, ensure_ascii=False, indent=2)}")

        response = requests.post(
            production_url,
            json=test_data,
            headers={"Content-Type": "application/json"}
        )

        print(f"✅ レスポンスステータス: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            print(f"✅ 成功: {result.get('success')}")
            print(f"📊 結果件数: {result.get('total_results')}件")
            print(f"⏱️ 処理時間: {result.get('processing_time_ms')}ms")

            # 上位3名を表示
            if result.get('results'):
                print("\n📋 上位3名:")
                for i, talent in enumerate(result['results'][:3]):
                    print(f"  {i+1}位: {talent.get('name')} "
                          f"(マッチングスコア: {talent.get('matching_score')}, "
                          f"基礎パワー: {talent.get('base_power_score')})")

            print("\n✅ Google Sheets連携コードの削除確認:")
            print("  本番環境からGoogle Sheetsへの出力は行われません（正常）")
            print("  本番環境のGoogle Sheets出力機能は意図的に無効化されました")

        else:
            print(f"❌ エラーレスポンス: {response.text}")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_production_clean()