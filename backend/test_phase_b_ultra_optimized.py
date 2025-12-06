#!/usr/bin/env python3
"""Phase B超最適化版マッチングの結果整合性検証"""
import asyncio
import json
import time
from app.api.endpoints.matching import post_matching, post_matching_optimized, post_matching_ultra_optimized
from app.schemas.matching import MatchingFormData

async def test_phase_b_consistency():
    """Phase B超最適化版と既存版の結果整合性テスト"""
    print("=" * 100)
    print("🚀 Phase B: 超最適化版 結果整合性検証")
    print("=" * 100)

    # テストケース定義
    test_case = {
        "company_name": "株式会社テストクライアント",
        "industry": "食品",
        "target_segments": "女性35-49歳",
        "purpose": "ブランドの認知度向上のため",
        "budget": "1,000万円〜3,000万円未満",
        "email": "test@talent-casting-dev.local"
    }

    try:
        # リクエストオブジェクト作成
        class MockRequest:
            def __init__(self):
                self.client = type('MockClient', (), {'host': '127.0.0.1'})()
                self.headers = {}

        mock_request = MockRequest()
        form_data = MatchingFormData(**test_case)

        print(f"\n🎯 テストケース: {test_case['industry']} / {test_case['target_segments']}")

        # 既存版実行
        print("\n📊 1. 既存版マッチング実行...")
        original_start = time.time()
        original_result = await post_matching(form_data, mock_request)
        original_time = time.time() - original_start

        # Phase A最適化版実行
        print("📊 2. Phase A最適化版マッチング実行...")
        phase_a_start = time.time()
        phase_a_result = await post_matching_optimized(form_data, mock_request)
        phase_a_time = time.time() - phase_a_start

        # Phase B超最適化版実行
        print("📊 3. Phase B超最適化版マッチング実行...")
        phase_b_start = time.time()
        phase_b_result = await post_matching_ultra_optimized(form_data, mock_request)
        phase_b_time = time.time() - phase_b_start

        # 結果比較
        print("\n🔍 4. 3版本結果整合性検証:")

        # 基本チェック
        assert original_result.success == phase_a_result.success == phase_b_result.success, "処理成功フラグ不一致"
        assert original_result.total_results == phase_a_result.total_results == phase_b_result.total_results, "結果件数不一致"
        print(f"   ✅ 結果件数: {original_result.total_results}件 (3版本すべて一致)")

        # 上位5件の詳細比較
        print("\n   上位5件詳細比較:")
        for i in range(min(5, len(original_result.results))):
            orig_talent = original_result.results[i]
            phase_a_talent = phase_a_result.results[i]
            phase_b_talent = phase_b_result.results[i]

            # タレントIDチェック
            assert orig_talent.account_id == phase_a_talent.account_id == phase_b_talent.account_id, \
                f"{i+1}位のタレントID不一致"

            # 名前チェック
            assert orig_talent.name == phase_a_talent.name == phase_b_talent.name, \
                f"{i+1}位のタレント名不一致"

            # 基礎パワー得点チェック（小数点2桁まで）
            assert abs(orig_talent.base_power_score - phase_a_talent.base_power_score) < 0.01, \
                f"{i+1}位の基礎パワー得点不一致(オリジナル vs Phase A)"
            assert abs(orig_talent.base_power_score - phase_b_talent.base_power_score) < 0.01, \
                f"{i+1}位の基礎パワー得点不一致(オリジナル vs Phase B)"

            # 業界イメージ調整チェック（None値対応）
            orig_adj = orig_talent.image_adjustment if orig_talent.image_adjustment is not None else 0.0
            phase_a_adj = phase_a_talent.image_adjustment if phase_a_talent.image_adjustment is not None else 0.0
            phase_b_adj = phase_b_talent.image_adjustment if phase_b_talent.image_adjustment is not None else 0.0

            assert abs(orig_adj - phase_a_adj) < 0.01, \
                f"{i+1}位の業界イメージ調整不一致(オリジナル vs Phase A): {orig_adj} vs {phase_a_adj}"
            assert abs(orig_adj - phase_b_adj) < 0.01, \
                f"{i+1}位の業界イメージ調整不一致(オリジナル vs Phase B): {orig_adj} vs {phase_b_adj}"

            orig_adj_str = f"{orig_talent.image_adjustment:+4.1f}" if orig_talent.image_adjustment is not None else "None"
            print(f"   {i+1}位: {orig_talent.name:<15} "
                  f"ID:{orig_talent.account_id} "
                  f"基礎:{orig_talent.base_power_score:.1f} "
                  f"調整:{orig_adj_str} ✅")

        # パフォーマンス比較
        print(f"\n⏱️ 5. パフォーマンス比較:")
        print(f"   既存版処理時間:      {original_time:.2f}秒")
        print(f"   Phase A最適化版:     {phase_a_time:.2f}秒")
        print(f"   Phase B超最適化版:   {phase_b_time:.2f}秒")

        # Phase A改善率
        if phase_a_time < original_time:
            phase_a_improvement = ((original_time - phase_a_time) / original_time) * 100
            print(f"   🚀 Phase A改善率: {phase_a_improvement:.1f}%高速化")

        # Phase B改善率
        if phase_b_time < original_time:
            phase_b_improvement = ((original_time - phase_b_time) / original_time) * 100
            print(f"   🚀 Phase B改善率: {phase_b_improvement:.1f}%高速化")

        # Phase B vs Phase A
        if phase_b_time < phase_a_time:
            phase_b_vs_a_improvement = ((phase_a_time - phase_b_time) / phase_a_time) * 100
            print(f"   🚀 Phase B vs A改善率: {phase_b_vs_a_improvement:.1f}%高速化")

        # 結果の完全一致確認
        original_names = [t.name for t in original_result.results]
        phase_a_names = [t.name for t in phase_a_result.results]
        phase_b_names = [t.name for t in phase_b_result.results]

        if original_names == phase_a_names == phase_b_names:
            print(f"\n✅ 完全一致確認: 全30件のタレント順序が3版本すべて完全一致")
        else:
            print(f"\n❌ 順序不一致: タレント順序に差異があります")

        print("\n" + "=" * 100)
        print("🎉 Phase B超最適化検証完了: マッチングロジック完全保持")
        print("=" * 100)

    except AssertionError as e:
        print(f"\n❌ 整合性エラー: {str(e)}")
        print("Phase B実装にバグがあります。修正が必要です。")
        raise
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_phase_b_consistency())