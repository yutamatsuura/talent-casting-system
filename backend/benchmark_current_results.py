#!/usr/bin/env python3
"""Phase A最適化前の現在の結果をベンチマーク保存"""
import asyncio
import json
import time
from datetime import datetime
from app.db.connection import get_asyncpg_connection
from app.api.endpoints.matching import post_matching
from app.schemas.matching import MatchingFormData
from fastapi import Request

async def benchmark_current_results():
    """最適化前の現在の結果を保存"""
    print("=" * 80)
    print("📊 Phase A最適化前ベンチマーク実行")
    print("=" * 80)

    # テストケース定義（MatchingFormDataスキーマ準拠）
    test_cases = [
        {
            "name": "化粧品_女性20-34_5000万円",
            "company_name": "株式会社テストクライアント",
            "industry": "化粧品・ヘアケア・オーラルケア",
            "target_segments": "女性20-34歳",
            "purpose": "商品サービスの特長訴求のため",
            "budget": "3,000万円〜5,000万円未満",
            "email": "test@talent-casting-dev.local"
        },
        {
            "name": "医薬品_男性20-34_1億円以上",
            "company_name": "株式会社テストクライアント",
            "industry": "医薬品・医療・健康食品",
            "target_segments": "男性20-34歳",
            "purpose": "商品サービスの特長訴求のため",
            "budget": "1億円以上",
            "email": "test@talent-casting-dev.local"
        },
        {
            "name": "食品_女性35-49_1000万円台",
            "company_name": "株式会社テストクライアント",
            "industry": "食品・飲料・酒類",
            "target_segments": "女性35-49歳",
            "purpose": "ブランドの認知度向上のため",
            "budget": "1,000万円〜3,000万円未満",
            "email": "test@talent-casting-dev.local"
        }
    ]

    benchmark_results = []

    for test_case in test_cases:
        print(f"\n🧪 テストケース: {test_case['name']}")

        # タイミング測定開始
        start_time = time.time()

        try:
            # リクエストオブジェクト作成
            class MockRequest:
                def __init__(self):
                    self.client = type('MockClient', (), {'host': '127.0.0.1'})()
                    self.headers = {}

            mock_request = MockRequest()

            # MatchingFormData作成
            form_data = MatchingFormData(**test_case)

            # 現在のマッチングAPI実行
            result = await post_matching(form_data, mock_request)

            end_time = time.time()
            processing_time = end_time - start_time

            print(f"   処理時間: {processing_time:.2f}秒")
            print(f"   結果数: {len(result.results if hasattr(result, 'results') else [])}件")

            # ベンチマーク結果保存
            benchmark_result = {
                "test_case": test_case,
                "processing_time": processing_time,
                "result_count": len(result.results if hasattr(result, 'results') else []),
                "top_5_talents": []
            }

            # 上位5位のタレント詳細保存
            results_list = result.results if hasattr(result, 'results') else []
            for i, talent in enumerate(results_list[:5]):
                # Pydanticオブジェクトまたは辞書を処理
                if hasattr(talent, 'name'):
                    name = talent.name
                    matching_score = talent.matching_score
                    base_power_score = getattr(talent, 'base_power_score', 0)
                    image_adjustment = getattr(talent, 'image_adjustment', 0)
                    account_id = getattr(talent, 'account_id', 0)
                else:
                    name = talent.get('name', '')
                    matching_score = talent.get('matching_score', 0)
                    base_power_score = talent.get('base_power_score', 0)
                    image_adjustment = talent.get('image_adjustment', 0)
                    account_id = talent.get('account_id', 0)

                benchmark_result["top_5_talents"].append({
                    "rank": i + 1,
                    "name": name,
                    "matching_score": matching_score,
                    "base_power_score": base_power_score,
                    "image_adjustment": image_adjustment,
                    "account_id": account_id
                })
                print(f"   {i+1}位: {name:<15} "
                      f"スコア:{matching_score:5.1f} "
                      f"(基礎:{base_power_score:5.1f} "
                      f"調整:{image_adjustment:+4.1f})")

            benchmark_results.append(benchmark_result)

        except Exception as e:
            print(f"   ❌ エラー: {str(e)}")
            benchmark_results.append({
                "test_case": test_case,
                "error": str(e),
                "processing_time": None
            })

    # 結果をJSONファイルに保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"benchmark_before_optimization_{timestamp}.json"

    benchmark_data = {
        "timestamp": timestamp,
        "description": "Phase A最適化実装前のベンチマーク結果",
        "test_cases": benchmark_results,
        "summary": {
            "total_test_cases": len(test_cases),
            "successful_cases": len([r for r in benchmark_results if "error" not in r]),
            "average_processing_time": sum([r.get("processing_time", 0) for r in benchmark_results if "error" not in r]) / max(len([r for r in benchmark_results if "error" not in r]), 1)
        }
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(benchmark_data, f, ensure_ascii=False, indent=2)

    print(f"\n📄 ベンチマーク結果保存完了: {filename}")
    print(f"   成功ケース: {benchmark_data['summary']['successful_cases']}/{benchmark_data['summary']['total_test_cases']}")
    print(f"   平均処理時間: {benchmark_data['summary']['average_processing_time']:.2f}秒")
    print("=" * 80)

    return filename

if __name__ == "__main__":
    asyncio.run(benchmark_current_results())