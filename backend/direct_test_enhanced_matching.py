#!/usr/bin/env python3
"""
enhanced_matching_debugの直接テスト
実際のマッチング結果を確認
"""
import asyncio
from app.services.enhanced_matching_debug import EnhancedMatchingDebug

async def test_enhanced_matching():
    print("🔍 enhanced_matching_debug直接テスト")
    print("=" * 50)

    try:
        # インスタンス作成
        debug_service = EnhancedMatchingDebug()

        # 内部メソッドを直接呼び出し
        results = await debug_service._execute_enhanced_matching(
            industry="化粧品・ヘアケア・オーラルケア",
            target_segment="女性20-34歳",
            budget="1,000万円〜3,000万円未満"
        )

        print(f"✅ 取得件数: {len(results)}件")

        if results:
            print("\n📊 上位5名のデータ:")
            print("順位 | タレント名     | VR人気度 | TPRスコア | 従来スコア")
            print("-" * 65)

            for i, result in enumerate(results[:5]):
                ranking = i + 1
                name = result.get("タレント名", "Unknown")[:10].ljust(10)
                vr_pop = result.get("VR人気度", 0)
                tpr_score = result.get("TPRスコア", 0)
                legacy_score = result.get("従来スコア", 0)

                print(f"{ranking:>4} | {name} | {vr_pop:>8.1f} | {tpr_score:>8.1f} | {legacy_score:>9.2f}")

                # 計算確認
                expected = (vr_pop + tpr_score) / 2
                if abs(legacy_score - expected) > 0.01:
                    print(f"     ⚠️  計算エラー: 期待値={expected:.2f}, 実際={legacy_score:.2f}")
                else:
                    print(f"     ✅ 計算正常: (VR + TPR) / 2 = {expected:.2f}")

            print(f"\n📈 全データサマリー:")
            print(f"   VR人気度平均: {sum(r.get('VR人気度', 0) for r in results) / len(results):.2f}")
            print(f"   TPRスコア平均: {sum(r.get('TPRスコア', 0) for r in results) / len(results):.2f}")
            print(f"   従来スコア平均: {sum(r.get('従来スコア', 0) for r in results) / len(results):.2f}")
        else:
            print("❌ データが取得できませんでした")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_matching())