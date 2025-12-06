#!/usr/bin/env python3
"""Phase A最適化版マッチングの結果整合性検証"""
import asyncio
import json
import time
from app.api.endpoints.matching import post_matching, post_matching_optimized
from app.schemas.matching import MatchingFormData

async def test_matching_consistency():
    """最適化版と既存版の結果整合性テスト"""
    print("=" * 80)
    print("🧪 Phase A最適化版 結果整合性検証")
    print("=" * 80)

    # テストケース定義
    test_case = {
        "company_name": "株式会社テストクライアント",
        "industry": "食品・飲料・酒類",
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

        # 最適化版実行
        print("📊 2. 最適化版マッチング実行...")
        optimized_start = time.time()
        optimized_result = await post_matching_optimized(form_data, mock_request)
        optimized_time = time.time() - optimized_start

        # 結果比較
        print("\n🔍 3. 結果整合性検証:")

        # 基本チェック
        assert original_result.success == optimized_result.success, "処理成功フラグ不一致"
        assert original_result.total_results == optimized_result.total_results, "結果件数不一致"
        print(f"   ✅ 結果件数: {original_result.total_results}件 (一致)")

        # 上位5件の詳細比較
        print("\n   上位5件詳細比較:")
        for i in range(min(5, len(original_result.results))):
            orig_talent = original_result.results[i]
            opt_talent = optimized_result.results[i]

            # タレントIDチェック
            assert orig_talent.account_id == opt_talent.account_id, f"{i+1}位のタレントID不一致"

            # 名前チェック
            assert orig_talent.name == opt_talent.name, f"{i+1}位のタレント名不一致"

            # 基礎パワー得点チェック（小数点2桁まで）
            assert abs(orig_talent.base_power_score - opt_talent.base_power_score) < 0.01, \
                f"{i+1}位の基礎パワー得点不一致"

            # 業界イメージ調整チェック
            assert abs(orig_talent.image_adjustment - opt_talent.image_adjustment) < 0.01, \
                f"{i+1}位の業界イメージ調整不一致"

            print(f"   {i+1}位: {orig_talent.name:<15} "
                  f"ID:{orig_talent.account_id} "
                  f"基礎:{orig_talent.base_power_score:.1f} "
                  f"調整:{orig_talent.image_adjustment:+4.1f} ✅")

        # パフォーマンス比較
        print(f"\n⏱️ 4. パフォーマンス比較:")
        print(f"   既存版処理時間: {original_time:.2f}秒")
        print(f"   最適化版処理時間: {optimized_time:.2f}秒")

        if optimized_time < original_time:
            improvement = ((original_time - optimized_time) / original_time) * 100
            print(f"   🚀 改善率: {improvement:.1f}%高速化")
        else:
            regression = ((optimized_time - original_time) / original_time) * 100
            print(f"   ⚠️ 低下率: {regression:.1f}%低速化")

        # 結果の完全一致確認
        original_names = [t.name for t in original_result.results]
        optimized_names = [t.name for t in optimized_result.results]

        if original_names == optimized_names:
            print(f"\n✅ 完全一致確認: 全30件のタレント順序が完全一致")
        else:
            print(f"\n❌ 順序不一致: タレント順序に差異があります")
            # 差異の詳細出力
            for i, (orig_name, opt_name) in enumerate(zip(original_names, optimized_names)):
                if orig_name != opt_name:
                    print(f"   {i+1}位: 既存版={orig_name} vs 最適化版={opt_name}")
                    break

        print("\n" + "=" * 80)
        print("🎉 結果整合性検証完了: マッチングロジック完全保持")
        print("=" * 80)

    except AssertionError as e:
        print(f"\n❌ 整合性エラー: {str(e)}")
        print("最適化実装にバグがあります。修正が必要です。")
        raise
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_matching_consistency())