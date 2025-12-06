#!/usr/bin/env python3
"""Phase B結果デバッグスクリプト"""
import asyncio
import json
from app.api.endpoints.matching import post_matching, post_matching_optimized, post_matching_ultra_optimized
from app.schemas.matching import MatchingFormData

async def debug_phase_b_results():
    """Phase B結果の詳細比較"""
    print("=" * 80)
    print("🔍 Phase B 結果詳細デバッグ")
    print("=" * 80)

    # テストケース
    test_case = {
        "company_name": "株式会社テストクライアント",
        "industry": "食品",
        "target_segments": "女性35-49歳",
        "purpose": "ブランドの認知度向上のため",
        "budget": "1,000万円〜3,000万円未満",
        "email": "test@talent-casting-dev.local"
    }

    class MockRequest:
        def __init__(self):
            self.client = type('MockClient', (), {'host': '127.0.0.1'})()
            self.headers = {}

    mock_request = MockRequest()
    form_data = MatchingFormData(**test_case)

    try:
        # 各版本の実行
        print("📊 実行中...")
        original_result = await post_matching(form_data, mock_request)
        phase_a_result = await post_matching_optimized(form_data, mock_request)
        phase_b_result = await post_matching_ultra_optimized(form_data, mock_request)

        print(f"✅ 実行完了")
        print(f"   Original: {len(original_result.results)}件")
        print(f"   Phase A:  {len(phase_a_result.results)}件")
        print(f"   Phase B:  {len(phase_b_result.results)}件")

        # 上位3件の詳細比較
        print("\n🔍 上位3件詳細データ比較:")
        for i in range(min(3, len(original_result.results))):
            orig = original_result.results[i]
            phase_a = phase_a_result.results[i]
            phase_b = phase_b_result.results[i]

            print(f"\n--- {i+1}位 ---")
            print(f"オリジナル: {orig.account_id} | {orig.name} | base: {orig.base_power_score} | adj: {orig.image_adjustment} | rec: {orig.is_recommended}")
            print(f"Phase A:    {phase_a.account_id} | {phase_a.name} | base: {phase_a.base_power_score} | adj: {phase_a.image_adjustment} | rec: {phase_a.is_recommended}")
            print(f"Phase B:    {phase_b.account_id} | {phase_b.name} | base: {phase_b.base_power_score} | adj: {phase_b.image_adjustment} | rec: {phase_b.is_recommended}")

            # データ型チェック
            print(f"データ型チェック:")
            print(f"  orig base_power_score: {type(orig.base_power_score)} = {orig.base_power_score}")
            print(f"  phase_b base_power_score: {type(phase_b.base_power_score)} = {phase_b.base_power_score}")

    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_phase_b_results())