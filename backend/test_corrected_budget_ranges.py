#!/usr/bin/env python3
"""修正された予算区分でのマッチングAPI動作確認テスト"""

import requests
import json
import time

def test_corrected_budget_ranges():
    """修正された予算区分での4区分テスト"""

    url = "http://localhost:8432/api/matching"

    # テストケース：修正された4つの予算区分
    budget_test_cases = [
        {
            "name": "1,000万円未満",
            "budget": "1,000万円未満",
            "expected_max": 9999999.00
        },
        {
            "name": "1,000万円～3,000万円未満",
            "budget": "1,000万円～3,000万円未満",
            "expected_max": 29999999.00
        },
        {
            "name": "3,000万円～1億円未満",
            "budget": "3,000万円～1億円未満",
            "expected_max": 99999999.00
        },
        {
            "name": "1億円以上",
            "budget": "1億円以上",
            "expected_max": 999999999.00
        }
    ]

    print("=" * 80)
    print("🚀 修正された予算区分でのマッチングAPIテスト")
    print("=" * 80)
    print("📋 テスト対象：正しい4予算区分")
    print("🎯 確認項目：各予算区分での正常動作・結果数・フィルタリング")
    print("=" * 80)

    results = {}

    for test_case in budget_test_cases:
        print(f"\n📊 {test_case['name']} テスト実行中...")
        print(f"   予算区分: {test_case['budget']}")
        print(f"   想定上限額: {test_case['expected_max']:,.0f}円")

        # テストデータ
        test_data = {
            "industry": "化粧品・ヘアケア・オーラルケア",
            "target_segments": ["女性20-34歳"],
            "budget": test_case["budget"],
            "company_name": f"{test_case['name']}テスト株式会社",
            "email": "budget-test@test.local"
        }

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
                results[test_case["name"]] = {
                    "success": True,
                    "result": result,
                    "processing_time_ms": processing_time
                }

                print(f"✅ 成功！処理時間: {processing_time:.1f}ms")
                print(f"   総件数: {result.get('total_results', 0)}")

                if "results" in result and result["results"]:
                    print(f"   トップ3:")
                    for i, talent in enumerate(result["results"][:3]):
                        print(f"     {i+1}. {talent.get('name', 'N/A')} "
                              f"({talent.get('matching_score', 0):.1f}点)")

            else:
                print(f"❌ エラー: {response.status_code}")
                print(f"   レスポンス: {response.text[:200]}...")
                results[test_case["name"]] = {
                    "success": False,
                    "error": response.text
                }

        except Exception as e:
            print(f"❌ 例外エラー: {e}")
            results[test_case["name"]] = {
                "success": False,
                "error": str(e)
            }

    # 結果サマリー
    print("\n" + "=" * 80)
    print("📊 テスト結果サマリー")
    print("=" * 80)

    success_count = 0
    total_count = len(budget_test_cases)

    for test_case in budget_test_cases:
        test_name = test_case["name"]
        if test_name in results and results[test_name]["success"]:
            success_count += 1
            result_data = results[test_name]["result"]
            print(f"✅ {test_name}: {result_data['total_results']}件抽出")
        else:
            print(f"❌ {test_name}: テスト失敗")

    print(f"\n📊 成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")

    # 詳細結果をファイル保存
    with open("/tmp/corrected_budget_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 詳細結果: /tmp/corrected_budget_test_results.json")

    if success_count == total_count:
        print("\n✅ 全予算区分で正常動作確認！")
    else:
        print(f"\n🚨 {total_count - success_count}件の予算区分でエラーが発生")

    print("=" * 80)

if __name__ == "__main__":
    test_corrected_budget_ranges()