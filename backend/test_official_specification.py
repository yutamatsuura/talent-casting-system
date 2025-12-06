#!/usr/bin/env python3
"""正式仕様（1業種1イメージ + アルコール年齢フィルタ）動作確認テスト"""

import requests
import json
import time

def test_official_matching():
    """正式仕様での複数業種マッチングテスト"""

    url = "http://localhost:8432/api/matching"

    # テストケース1: アルコール業界（年齢フィルタ適用）
    alcohol_test = {
        "industry": "アルコール飲料",
        "target_segments": ["男性20-34"],
        "budget": "1,000万円～3,000万円未満",
        "company_name": "アルコールテスト株式会社",
        "email": "alcohol@test.local"
    }

    # テストケース2: 化粧品業界（年齢フィルタなし）
    cosmetics_test = {
        "industry": "化粧品・ヘアケア・オーラルケア",
        "target_segments": ["女性20-34"],
        "budget": "1,000万円～3,000万円未満",
        "company_name": "コスメテスト株式会社",
        "email": "cosmetics@test.local"
    }

    # テストケース3: ゲーム業界（年齢フィルタなし）
    game_test = {
        "industry": "ゲーム・エンターテイメント・アプリ",
        "target_segments": ["男性12-19"],
        "budget": "1,000万円～3,000万円未満",
        "company_name": "ゲームテスト株式会社",
        "email": "game@test.local"
    }

    test_cases = [
        ("アルコール業界（25歳以上フィルタ）", alcohol_test),
        ("化粧品業界（通常フィルタ）", cosmetics_test),
        ("ゲーム業界（通常フィルタ）", game_test)
    ]

    print("=" * 80)
    print("🚀 正式仕様マッチングAPIテスト（1業種1イメージ + アルコール年齢フィルタ）")
    print("=" * 80)

    results = {}

    for test_name, test_data in test_cases:
        print(f"\n📊 {test_name} テスト実行中...")
        print(f"   業種: {test_data['industry']}")
        print(f"   ターゲット: {test_data['target_segments'][0]}")

        try:
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
                results[test_name] = result

                print(f"✅ 成功！処理時間: {processing_time:.1f}ms")
                print(f"   総件数: {result.get('total_results', 0)}")

                if "results" in result and result["results"]:
                    top_talent = result["results"][0]
                    print(f"   1位: {top_talent.get('name', 'N/A')} ({top_talent.get('matching_score', 0):.1f}点)")
                    print(f"   基礎パワー: {top_talent.get('base_power_score', 0):.1f}")
                    print(f"   イメージ調整: {top_talent.get('image_adjustment', 0)}")

            else:
                print(f"❌ エラー: {response.status_code}")
                print(f"   レスポンス: {response.text[:200]}...")

        except Exception as e:
            print(f"❌ 例外エラー: {e}")

    # 結果比較分析
    print("\n" + "=" * 80)
    print("📊 結果比較分析")
    print("=" * 80)

    for test_name, result in results.items():
        if result and "results" in result:
            print(f"\n🔍 {test_name}:")
            print(f"   総件数: {result['total_results']}")
            print(f"   処理時間: {result.get('processing_time_ms', 0):.1f}ms")

            # 年齢分布分析（アルコール業界の場合）
            if "アルコール" in test_name:
                print("   🚨 年齢フィルタリング確認: 25歳以上のみ抽出されているか")

            # トップ3表示
            print("   トップ3:")
            for i, talent in enumerate(result["results"][:3]):
                print(f"     {i+1}. {talent.get('name', 'N/A')} "
                      f"({talent.get('matching_score', 0):.1f}点)")

    # ファイル保存
    with open("/tmp/official_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 詳細結果を /tmp/official_test_results.json に保存")
    print("\n" + "=" * 80)
    print("✅ 正式仕様テスト完了")
    print("=" * 80)

if __name__ == "__main__":
    test_official_matching()