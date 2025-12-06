#!/usr/bin/env python3
"""フロント・バックエンド・API修正要否確認"""

import requests
import json
import time

def test_api_endpoints():
    """全APIエンドポイントの動作確認"""

    base_url = "http://localhost:8432/api"

    print("=" * 80)
    print("🔍 API ENDPOINTS VERIFICATION")
    print("=" * 80)
    print("🎯 目的: マスタデータ修正後のAPI動作確認")
    print("=" * 80)

    results = {}

    # 1. Health Check
    print("\n💊 === HEALTH CHECK ===")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API Server: 正常稼働中")
            results["health"] = {"status": "OK", "response": response.json()}
        else:
            print(f"❌ API Server: エラー {response.status_code}")
            results["health"] = {"status": "ERROR", "code": response.status_code}
    except Exception as e:
        print(f"❌ API Server: 接続エラー {e}")
        results["health"] = {"status": "CONNECTION_ERROR", "error": str(e)}

    # 2. Industries Endpoint
    print("\n🏭 === INDUSTRIES ENDPOINT ===")
    try:
        response = requests.get(f"{base_url}/industries", timeout=10)
        if response.status_code == 200:
            industries = response.json()
            print(f"✅ 業種マスタ取得: {len(industries)}件")

            # 最初の5件表示
            print("📊 業種リスト (最初の5件):")
            for i, industry in enumerate(industries[:5]):
                print(f"   {industry['id']}: {industry['name']}")

            # 期待する20業種があるか確認
            expected_names = ["食品", "菓子・氷菓", "乳製品", "清涼飲料水", "アルコール飲料"]
            match_count = sum(1 for ind in industries[:5] if ind['name'] in expected_names)

            if len(industries) == 20 and match_count == 5:
                print("✅ 正しい20業種が正常に返されています")
                results["industries"] = {"status": "OK", "count": len(industries), "data": industries[:3]}
            else:
                print(f"⚠️ 業種データに問題の可能性: 件数={len(industries)}, 一致={match_count}/5")
                results["industries"] = {"status": "WARNING", "count": len(industries)}
        else:
            print(f"❌ 業種マスタ取得エラー: {response.status_code}")
            results["industries"] = {"status": "ERROR", "code": response.status_code}
    except Exception as e:
        print(f"❌ 業種マスタ取得例外: {e}")
        results["industries"] = {"status": "EXCEPTION", "error": str(e)}

    # 3. Target Segments Endpoint
    print("\n🎯 === TARGET SEGMENTS ENDPOINT ===")
    try:
        response = requests.get(f"{base_url}/target-segments", timeout=10)
        if response.status_code == 200:
            segments = response.json()
            print(f"✅ ターゲット層取得: {len(segments)}件")

            # 全件表示
            print("📊 ターゲット層リスト:")
            for segment in segments:
                print(f"   {segment['id']}: {segment['name']} ({segment['code']})")

            # 期待する8セグメントがあるか確認
            expected_codes = ["M1219", "M2034", "M3549", "M5069", "F1219", "F2034", "F3549", "F5069"]
            actual_codes = [seg['code'] for seg in segments]
            missing_codes = [code for code in expected_codes if code not in actual_codes]

            if len(segments) == 8 and not missing_codes:
                print("✅ 正しい8セグメントが正常に返されています")
                results["target_segments"] = {"status": "OK", "count": len(segments), "codes": actual_codes}
            else:
                print(f"⚠️ ターゲット層データに問題: 件数={len(segments)}, 不足={missing_codes}")
                results["target_segments"] = {"status": "WARNING", "count": len(segments), "missing": missing_codes}
        else:
            print(f"❌ ターゲット層取得エラー: {response.status_code}")
            results["target_segments"] = {"status": "ERROR", "code": response.status_code}
    except Exception as e:
        print(f"❌ ターゲット層取得例外: {e}")
        results["target_segments"] = {"status": "EXCEPTION", "error": str(e)}

    # 4. Matching API Test
    print("\n🚀 === MATCHING API TEST ===")
    try:
        # 修正されたマスタデータでテスト
        test_data = {
            "industry": "化粧品・ヘアケア・オーラルケア",  # 業種ID 8
            "target_segments": ["女性20-34歳"],  # F2034
            "budget": "1,000万円～3,000万円未満",  # 修正された予算区分
            "company_name": "整合性確認テスト株式会社",
            "email": "test@integrity-check.local"
        }

        start_time = time.time()
        response = requests.post(f"{base_url}/matching", json=test_data, timeout=30)
        end_time = time.time()
        processing_time = (end_time - start_time) * 1000

        if response.status_code == 200:
            result = response.json()
            print(f"✅ マッチングAPI: 正常動作")
            print(f"   処理時間: {processing_time:.1f}ms")
            print(f"   結果件数: {result.get('total_results', 0)}件")

            if "results" in result and result["results"]:
                top_talent = result["results"][0]
                print(f"   1位: {top_talent.get('name', 'N/A')} ({top_talent.get('matching_score', 0):.1f}点)")

            results["matching"] = {
                "status": "OK",
                "processing_time_ms": processing_time,
                "total_results": result.get('total_results', 0),
                "top_score": result["results"][0].get('matching_score', 0) if result.get("results") else 0
            }
        else:
            print(f"❌ マッチングAPIエラー: {response.status_code}")
            print(f"   エラー内容: {response.text[:200]}...")
            results["matching"] = {"status": "ERROR", "code": response.status_code, "error": response.text[:200]}
    except Exception as e:
        print(f"❌ マッチングAPI例外: {e}")
        results["matching"] = {"status": "EXCEPTION", "error": str(e)}

    # 結果サマリー
    print("\n" + "=" * 80)
    print("📊 API VERIFICATION SUMMARY")
    print("=" * 80)

    all_ok = True
    for endpoint, result in results.items():
        status = result.get("status", "UNKNOWN")
        if status == "OK":
            print(f"✅ {endpoint.upper()}: 正常")
        elif status == "WARNING":
            print(f"⚠️ {endpoint.upper()}: 警告")
            all_ok = False
        else:
            print(f"❌ {endpoint.upper()}: エラー")
            all_ok = False

    print("\n" + "=" * 80)
    if all_ok:
        print("🎉 全APIエンドポイント正常動作確認")
        print("✅ フロント・バック連携に問題なし")
        print("✅ API修正は不要です")
    else:
        print("🚨 一部APIエンドポイントに問題があります")
        print("🔧 該当部分の修正が必要です")
    print("=" * 80)

    # 詳細結果をファイル保存
    with open("/tmp/api_verification_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 詳細結果: /tmp/api_verification_results.json")

    return all_ok

if __name__ == "__main__":
    result = test_api_endpoints()
    exit(0 if result else 1)