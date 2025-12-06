#!/usr/bin/env python3
"""完全マッチングAPIテストスクリプト（業種修正後）"""

import requests
import json
import time

def test_matching_api():
    """化粧品・ヘアケア・オーラルケア × 女性20-34でマッチングテスト"""

    url = "http://localhost:8432/api/matching"

    test_data = {
        "industry": "化粧品・ヘアケア・オーラルケア",
        "target_segments": ["女性20-34"],
        "budget": "1,000万円～3,000万円未満",
        "company_name": "テスト株式会社",
        "email": "test@talent-casting-dev.local"
    }

    print("=== 完全マッチングAPIテスト（業種修正後） ===")
    print(f"📊 テスト条件:")
    print(f"   - 業種: 化粧品・ヘアケア・オーラルケア (ID: 8)")
    print(f"   - ターゲット: 女性20-34")
    print(f"   - 予算上限: 3,000万円")
    print(f"   - 起用目的: ブランド認知拡大")
    print()

    try:
        print("🚀 マッチングAPI呼び出し中...")
        start_time = time.time()

        response = requests.post(
            url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        end_time = time.time()
        processing_time = (end_time - start_time) * 1000

        if response.status_code == 200:
            result = response.json()
            print(f"✅ マッチングAPI成功！")
            print(f"⏱️  処理時間: {processing_time:.1f}ms")
            print()

            # 結果サマリー表示
            if "success" in result and result["success"]:
                print(f"📊 マッチング結果:")
                print(f"   - 成功: {result.get('success')}")
                print(f"   - 総件数: {result.get('total_results', 0)}")
                print(f"   - 処理時間: {result.get('processing_time_ms', 0):.1f}ms")
                print()

                # トップ5タレント表示
                if "results" in result and result["results"]:
                    print("🏆 トップ5タレント:")
                    for i, talent in enumerate(result["results"][:5]):
                        print(f"   {i+1}. {talent.get('name', 'N/A')} "
                              f"({talent.get('category', 'N/A')})")
                        print(f"      マッチングスコア: {talent.get('matching_score', 0):.1f}")
                        print(f"      基礎パワー: {talent.get('base_power_score', 0):.1f}")
                        print(f"      イメージ調整: {talent.get('image_adjustment', 0)}")
                        print()

                # 完全なレスポンスをファイルに保存
                with open("/tmp/matching_result.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print("💾 完全結果を /tmp/matching_result.json に保存")

            else:
                print(f"❌ マッチング失敗: {result}")

        else:
            print(f"❌ API呼び出し失敗")
            print(f"   ステータスコード: {response.status_code}")
            print(f"   レスポンス: {response.text}")

    except requests.exceptions.Timeout:
        print("⏰ タイムアウト（30秒）")
    except requests.exceptions.ConnectionError:
        print("🔌 接続エラー - APIサーバーが起動していません")
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    test_matching_api()