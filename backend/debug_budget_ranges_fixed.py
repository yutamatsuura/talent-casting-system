#!/usr/bin/env python3
"""
予算範囲テーブルの正しい構造確認
"""
import asyncio
import asyncpg

async def check_budget_ranges():
    """budget_rangesテーブルの内容確認"""
    print("=" * 80)
    print("🔍 予算範囲テーブル調査（修正版）")
    print("=" * 80)

    try:
        conn = await asyncpg.connect(
            host='ep-sparkling-smoke-a183z7h8-pooler.ap-southeast-1.aws.neon.tech',
            user='neondb_owner',
            password='npg_5X1MlRZzVheF',
            database='neondb',
            ssl='require'
        )

        # まずテーブル構造を確認
        print("📋 budget_rangesテーブル構造:")
        schema_query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'budget_ranges'
        ORDER BY ordinal_position
        """
        schema_rows = await conn.fetch(schema_query)

        if schema_rows:
            for row in schema_rows:
                print(f"   {row['column_name']}: {row['data_type']}")
        else:
            print("   テーブルが見つかりません")

        # budget_rangesテーブルの全内容を確認（構造不明なので全カラム取得）
        print(f"\n📊 budget_rangesテーブルの内容:")
        budget_query = "SELECT * FROM budget_ranges"
        budget_rows = await conn.fetch(budget_query)

        if budget_rows:
            for i, row in enumerate(budget_rows):
                print(f"   行 {i+1}: {dict(row)}")
        else:
            print("   データがありません")

        # テスト用予算文字列でのマッチング確認
        test_budgets = ["1,000万円未満", "1億円以上"]

        print(f"\n🧪 予算マッチングテスト:")
        for budget in test_budgets:
            print(f"\n   テスト予算: '{budget}'")

            # 現在の処理と同じクエリを実行
            match_query = """
            SELECT * FROM budget_ranges
            WHERE REPLACE(REPLACE(REPLACE(range_name, '～', '〜'), ' ', ''), '　', '') =
                  REPLACE(REPLACE(REPLACE($1, '～', '〜'), ' ', ''), '　', '')
            """
            match_result = await conn.fetch(match_query, budget)

            if match_result:
                for match in match_result:
                    print(f"     ✅ マッチ: {dict(match)}")
            else:
                print(f"     ❌ マッチなし")

        await conn.close()

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_budget_ranges())