#!/usr/bin/env python3
"""
元のサービスと修正後のサービスを比較
なぜ結果数が変わったのかを特定
"""
import requests
import json

def test_both_services():
    """元のサービスと修正後のサービスを比較"""
    print("=" * 80)
    print("🔍 元サービス vs 修正後サービス比較")
    print("=" * 80)

    # 同じテストデータ
    test_data = {
        "industry": "ファッション",
        "target_segments": "女性20-34歳",
        "budget": "1,000万円～3,000万円未満",
        "purpose": "商品・サービスの特長訴求のため",
        "company_name": "比較テスト企業",
        "email": "test@example.com",
        "phone": "03-1234-5678"
    }

    services = [
        {
            "name": "元のサービス（修正前）",
            "url": "https://talent-casting-backend-392592761218.asia-northeast1.run.app"
        },
        {
            "name": "修正後サービス",
            "url": "https://talent-casting-backend-fixed-392592761218.asia-northeast1.run.app"
        }
    ]

    results = {}

    for service in services:
        print(f"\n📊 {service['name']} をテスト")
        print(f"   URL: {service['url']}/api/matching")

        try:
            response = requests.post(
                f"{service['url']}/api/matching",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            print(f"   レスポンス: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                talent_count = len(data.get('results', []))
                total_results = data.get('total_results', 0)

                print(f"   ✅ 取得タレント数: {talent_count}名")
                print(f"   📊 total_results: {total_results}")

                # 上位3名の名前を記録
                top_3_names = []
                for i, talent in enumerate(data.get('results', [])[:3]):
                    name = talent.get('name', 'N/A')
                    score = talent.get('matching_score', 'N/A')
                    is_recommended = talent.get('is_recommended', False)
                    top_3_names.append(f"{name}({score}点{'★' if is_recommended else ''})")

                print(f"   🏆 上位3名: {', '.join(top_3_names)}")

                # 新垣結衣チェック
                aragaki_found = False
                for talent in data.get('results', []):
                    if '新垣' in talent.get('name', ''):
                        aragaki_found = True
                        print(f"   ❌ 新垣結衣発見: {talent.get('name')} (スコア: {talent.get('matching_score')})")

                if not aragaki_found:
                    print(f"   ✅ 新垣結衣は除外されています")

                results[service['name']] = {
                    'count': talent_count,
                    'total_results': total_results,
                    'top_3': top_3_names,
                    'aragaki_found': aragaki_found,
                    'status': 'success'
                }

            else:
                print(f"   ❌ エラー: {response.status_code}")
                print(f"   メッセージ: {response.text[:200]}")
                results[service['name']] = {
                    'status': 'error',
                    'error_code': response.status_code,
                    'error_message': response.text[:200]
                }

        except Exception as e:
            print(f"   ❌ 接続エラー: {e}")
            results[service['name']] = {
                'status': 'connection_error',
                'error': str(e)
            }

    # 比較結果
    print(f"\n" + "=" * 80)
    print(f"📈 比較結果")
    print(f"=" * 80)

    for service_name, result in results.items():
        print(f"\n🔍 {service_name}:")
        if result['status'] == 'success':
            print(f"   タレント数: {result['count']}名")
            print(f"   新垣結衣: {'除外済み' if not result['aragaki_found'] else '含まれている❌'}")
        else:
            print(f"   状態: {result['status']}")

    # 差異分析
    if len(results) == 2:
        service_names = list(results.keys())
        result1 = results[service_names[0]]
        result2 = results[service_names[1]]

        if result1['status'] == 'success' and result2['status'] == 'success':
            count1 = result1['count']
            count2 = result2['count']

            print(f"\n🔍 差異分析:")
            print(f"   {service_names[0]}: {count1}名")
            print(f"   {service_names[1]}: {count2}名")
            print(f"   差分: {abs(count1 - count2)}名")

            if count1 != count2:
                print(f"   🚨 タレント数が変化しています！")
                print(f"   💡 考えられる原因:")
                print(f"      1. 予算フィルタリングロジックの意図しない副作用")
                print(f"      2. おすすめタレント統合機能の動作変化")
                print(f"      3. データベース接続の違い")
                print(f"      4. フォールバック処理の有無")

    print(f"\n" + "=" * 80)

if __name__ == "__main__":
    test_both_services()