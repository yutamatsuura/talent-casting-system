#!/usr/bin/env python3
"""
Google Sheets用データ取得テスト（修正版）
VR人気度、TPRスコア、従来スコア（基礎パワー得点）の表示確認
"""
import asyncio
from app.services.enhanced_matching_debug import EnhancedMatchingDebug

async def test_sheets_data():
    print("🔍 Google Sheets用データ取得テスト")
    print("=" * 50)

    try:
        # EnhancedMatchingDebugインスタンス作成
        debug_service = EnhancedMatchingDebug()

        # テスト実行（正しい条件）
        results = await debug_service.generate_complete_talent_analysis(
            industry="乳製品",
            target_segments=["男性12-19歳"],
            budget="1,000万円〜3,000万円未満",
            purpose="商品サービスの特長訴求のため"
        )

        print(f"✅ 取得件数: {len(results)}件")

        # データ構造確認
        if results and len(results) > 0:
            print(f"データ構造: {type(results[0])}")
            if isinstance(results[0], dict):
                print(f"キー一覧: {list(results[0].keys())}")

            print("\n📊 上位5名のデータ確認:")
            print("順位 | タレント名 | VR人気度 | TPRスコア | 従来スコア | 従来順位 | 最終スコア")
            print("-" * 80)

            for i, result in enumerate(results[:5]):
                ranking = i + 1
                name = result.get("タレント名", "")
                vr = result.get("VR人気度", 0)
                tpr = result.get("TPRスコア", 0)
                base = result.get("従来スコア", 0)
                conventional_rank = result.get("従来順位", 0)
                final_score = result.get("最終スコア", 0)
                print(f"{ranking:>4} | {name:10} | {vr:8.1f} | {tpr:8.1f} | {base:8.1f} | {conventional_rank:3} | {final_score:8.3f}")

                # 最終スコアの振り分け確認
                if ranking <= 3:
                    expected_range = "97.0-99.7"
                elif ranking <= 10:
                    expected_range = "93.0-96.9"
                elif ranking <= 20:
                    expected_range = "89.0-92.9"
                else:
                    expected_range = "86.0-88.9"
                print(f"        期待範囲: {expected_range}")

            # 新垣結衣を探す
            print("\n🔍 新垣結衣の確認:")
            gakki_found = False
            for i, result in enumerate(results):
                name = result.get("タレント名", "")
                if "新垣" in name:
                    ranking = i + 1
                    vr = result.get("VR人気度", 0)
                    tpr = result.get("TPRスコア", 0)
                    base = result.get("従来スコア", 0)
                    conventional_rank = result.get("従来順位", 0)
                    print(f"  最終順位: {ranking}位")
                    print(f"  タレント名: {name}")
                    print(f"  VR人気度: {vr}")
                    print(f"  TPRスコア: {tpr}")
                    print(f"  従来スコア: {base}")
                    print(f"  従来順位: {conventional_rank}位")
                    print(f"  計算確認: ({vr} + {tpr}) / 2 = {(vr + tpr) / 2}")
                    gakki_found = True
                    break

            if not gakki_found:
                print("  新垣結衣は30名の中に含まれていません")
        else:
            print("データが取得できませんでした")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sheets_data())