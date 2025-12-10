#!/usr/bin/env python3
"""
CSV診断エンドポイントのテスト
なぜ0になるかを確認
"""
import asyncio
import asyncpg
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def test_csv_endpoint_logic():
    """CSV診断エンドポイントのロジックを再現してテスト"""
    try:
        # データベースに接続
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            db_url = "postgresql://neondb_owner:npg_5X1MlRZzVheF@ep-sparkling-smoke-a183z7h8-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

        conn = await asyncpg.connect(db_url)

        # 最新のフォーム送信を取得
        query = "SELECT * FROM form_submissions ORDER BY created_at DESC LIMIT 1"
        result = await conn.fetch(query)

        if not result:
            print("📊 フォーム送信データが見つかりません")
            await conn.close()
            return

        submission = result[0]
        print(f"📊 テスト対象の送信データ:")
        print(f"   ID: {submission['id']}")
        print(f"   業種: {submission['industry']}")
        print(f"   ターゲット: {submission['target_segment']}")
        print(f"   予算: {submission['budget_range']}")
        print(f"   目的: {submission.get('usage_purpose', submission.get('purpose', 'N/A'))}")

        # enhanced_matching_debugと同じロジックを実行
        from app.services.enhanced_matching_debug import EnhancedMatchingDebug

        debug_matcher = EnhancedMatchingDebug()

        print(f"\n🔍 リアルタイム分析実行中...")
        detailed_results = await debug_matcher.generate_complete_talent_analysis(
            industry=submission['industry'],
            target_segments=[submission['target_segment']],
            purpose=submission.get('usage_purpose', submission.get('purpose', 'デフォルト')),
            budget=submission['budget_range']
        )

        print(f"✅ 分析完了: {len(detailed_results)}件のタレントデータ")

        if detailed_results:
            # 最初の5件の結果を表示
            print(f"\n📈 サンプル結果 (最初の5件):")
            for i, result in enumerate(detailed_results[:5], 1):
                print(f"{i}. タレント名: {result.get('タレント名', 'N/A')}")
                print(f"   VR人気度: {result.get('VR人気度', 'N/A')}")
                print(f"   TPRスコア: {result.get('TPRスコア', 'N/A')}")
                print(f"   従来スコア: {result.get('従来スコア', 'N/A')}")
                print(f"   おもしろさ: {result.get('おもしろさ', 'N/A')}")
                print(f"   清潔感: {result.get('清潔感', 'N/A')}")
                print(f"   最終スコア: {result.get('最終スコア', 'N/A')}")
                print(f"   最終順位: {result.get('最終順位', 'N/A')}")
                print()

            # 0の値がどれだけあるかチェック
            zero_count = 0
            total_fields = 0
            for result in detailed_results:
                for key, value in result.items():
                    if key in ['VR人気度', 'TPRスコア', '従来スコア', 'おもしろさ', '清潔感', '個性的な', '信頼できる', 'かわいい', 'カッコいい', '大人の魅力']:
                        total_fields += 1
                        if value == 0 or value == 0.0:
                            zero_count += 1

            print(f"📊 ゼロ値統計:")
            print(f"   総フィールド数: {total_fields}")
            print(f"   ゼロ値の数: {zero_count}")
            print(f"   ゼロ率: {zero_count/total_fields*100:.1f}%" if total_fields > 0 else "データなし")

        else:
            print("❌ 分析結果が空です")

        await conn.close()

    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_csv_endpoint_logic())