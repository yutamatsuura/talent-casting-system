#!/usr/bin/env python3
"""
復旧後のサービステスト
元のAPIサービスに戻したフロントエンドが正常に30名表示するか確認
"""
import requests
import json

def test_restored_service():
    """復旧後のAPIサービステスト"""
    print("=" * 80)
    print("🔄 復旧後サービステスト")
    print("=" * 80)

    # 復旧されたAPIサービス（元の正常動作版）
    api_url = "https://talent-casting-backend-392592761218.asia-northeast1.run.app"

    test_data = {
        "industry": "ファッション",
        "target_segments": "女性20-34歳",
        "budget": "1,000万円～3,000万円未満",
        "purpose": "商品・サービスの特長訴求のため",
        "company_name": "復旧確認テスト企業",
        "email": "test@example.com",
        "phone": "03-1234-5678"
    }

    print(f"📡 APIエンドポイント: {api_url}/api/matching")
    print(f"📋 フロントエンドURL: https://talent-casting-diagnosis-pbhqge864-yutamatsuuras-projects.vercel.app")

    try:
        # API直接テスト
        response = requests.post(
            f"{api_url}/api/matching",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        print(f"\n📊 APIレスポンス:")
        print(f"   ステータス: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            talent_count = len(data.get('results', []))
            total_results = data.get('total_results', 0)

            print(f"   ✅ 取得タレント数: {talent_count}名")
            print(f"   📊 total_results: {total_results}")

            # 新垣結衣チェック
            aragaki_found = False
            for talent in data.get('results', []):
                if '新垣' in talent.get('name', ''):
                    aragaki_found = True
                    print(f"   ❌ 新垣結衣が含まれています: {talent.get('name')} (スコア: {talent.get('matching_score')})")

            if not aragaki_found:
                print(f"   ✅ 新垣結衣は正しく除外されています")

            # 上位5名表示
            print(f"\n🏆 上位5名:")
            for i, talent in enumerate(data.get('results', [])[:5]):
                name = talent.get('name', 'N/A')
                score = talent.get('matching_score', 'N/A')
                is_recommended = talent.get('is_recommended', False)
                ranking = talent.get('ranking', i+1)
                print(f"   {ranking}位: {name} ({score}点{'★' if is_recommended else ''})")

            # 評価
            if talent_count == 30 and not aragaki_found:
                print(f"\n✅ 復旧成功！")
                print(f"   - タレント数: 30名 ✅")
                print(f"   - 新垣結衣除外: ✅")
                print(f"   - 本番環境が正常に機能しています")
            else:
                print(f"\n⚠️ 部分的な問題あり")
                if talent_count != 30:
                    print(f"   - タレント数が30名でない: {talent_count}名")
                if aragaki_found:
                    print(f"   - 新垣結衣が除外されていない")

        else:
            print(f"   ❌ APIエラー: {response.status_code}")
            print(f"   メッセージ: {response.text[:200]}")

    except Exception as e:
        print(f"❌ テストエラー: {e}")

    print(f"\n📱 フロントエンドテスト:")
    print(f"   URL: https://talent-casting-diagnosis-pbhqge864-yutamatsuuras-projects.vercel.app")
    print(f"   → 診断を実行して30名が表示されることを確認してください")

    print(f"\n" + "=" * 80)
    print(f"🎯 次のステップ:")
    print(f"   1. フロントエンドで診断実行 → 30名表示確認")
    print(f"   2. 問題がなければ、元のコードの分析を開始")
    print(f"   3. なぜ元のコードで30名表示されるのかを理解")
    print(f"   4. 予算フィルター修正を慎重に再実装")
    print(f"=" * 80)

if __name__ == "__main__":
    test_restored_service()