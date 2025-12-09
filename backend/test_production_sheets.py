#!/usr/bin/env python3
"""
本番環境Google Sheets連携テスト
"""
import requests
import json

def test_production_sheets_integration():
    print("🔍 本番環境Google Sheets連携テスト")
    print("=" * 50)

    # テストデータ
    test_data = {
        "industry": "乳製品",
        "target_segments": "男性12-19歳",
        "budget": "1,000万円〜3,000万円未満",
        "purpose": "商品サービスの特長訴求のため",
        "company_name": "株式会社本番テスト",
        "email": "production-test@example.com"
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

            print("\n🎯 Google Sheetsへのデータ出力:")
            print("  https://docs.google.com/spreadsheets/d/1lRsdHKJr8qxjbunlo7y7vYnN-jP3qdlgIdH7j9KooJc/edit")
            print("  ↑ このURLで結果が追加されているか確認してください")

        else:
            print(f"❌ エラーレスポンス: {response.text}")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_production_sheets_integration()