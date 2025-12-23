#!/usr/bin/env python3
"""
APIレスポンスの詳細を調査
固定の3名だけ表示される原因を特定
"""
import requests
import json

def debug_api_response():
    """APIレスポンスを詳細に調査"""
    base_url = "https://talent-casting-backend-fixed-392592761218.asia-northeast1.run.app"

    print("=" * 80)
    print("🔍 APIレスポンス詳細調査")
    print("=" * 80)

    test_data = {
        "industry": "ファッション",
        "target_segments": "女性20-34歳",
        "budget": "1,000万円～3,000万円未満",
        "purpose": "商品・サービスの特長訴求のため",
        "company_name": "テスト企業",
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
        print(f"📦 レスポンスヘッダー:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")

        if response.status_code == 200:
            data = response.json()

            print(f"\n📋 レスポンス構造:")
            print(f"   トップレベルキー: {list(data.keys())}")

            if 'results' in data:
                results = data['results']
                print(f"\n🎯 Results詳細:")
                print(f"   結果数: {len(results)}")
                print(f"   total_results: {data.get('total_results', 'N/A')}")

                for i, talent in enumerate(results):
                    print(f"\n   [{i+1}] {talent.get('name', 'N/A')}:")
                    for key, value in talent.items():
                        print(f"      {key}: {value}")

            # おすすめタレント関連フィールドがあるかチェック
            recommended_fields = ['recommended_talents', 'recommended', 'top_talents', 'featured']
            for field in recommended_fields:
                if field in data:
                    print(f"\n🌟 {field}が見つかりました:")
                    print(f"   内容: {data[field]}")

            # その他のフィールドも表示
            other_fields = [k for k in data.keys() if k not in ['results', 'success', 'total_results']]
            if other_fields:
                print(f"\n📝 その他のフィールド:")
                for field in other_fields:
                    print(f"   {field}: {data[field]}")

            print(f"\n📄 完全なレスポンス（整形版）:")
            print(json.dumps(data, ensure_ascii=False, indent=2))

        else:
            print(f"❌ APIエラー")
            print(f"   レスポンス: {response.text}")

    except Exception as e:
        print(f"❌ エラー: {e}")

    print("\n" + "=" * 80)
    print("🏁 調査完了")
    print("=" * 80)

if __name__ == "__main__":
    debug_api_response()