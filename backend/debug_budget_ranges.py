#!/usr/bin/env python3
"""
予算範囲テーブルの確認と予算マッチング問題の調査
"""
import asyncio
import asyncpg

async def check_budget_ranges():
    """budget_rangesテーブルの内容確認"""
    print("=" * 80)
    print("🔍 予算範囲テーブル調査")
    print("=" * 80)

    try:
        conn = await asyncpg.connect(
            host='ep-sparkling-smoke-a183z7h8-pooler.ap-southeast-1.aws.neon.tech',
            user='neondb_owner',
            password='npg_5X1MlRZzVheF',
            database='neondb',
            ssl='require'
        )

        # budget_rangesテーブルの全内容を確認
        print("📊 budget_rangesテーブルの内容:")
        budget_query = "SELECT * FROM budget_ranges ORDER BY id"
        budget_rows = await conn.fetch(budget_query)

        for row in budget_rows:
            print(f"   ID: {row['id']}, range_name: '{row['range_name']}', max_amount: {row['max_amount']}")

        # テスト用予算文字列でのマッチング確認
        test_budgets = ["1,000万円未満", "1億円以上"]

        print(f"\n🧪 予算マッチングテスト:")
        for budget in test_budgets:
            print(f"\n   テスト予算: '{budget}'")

            # 現在の処理と同じクエリを実行
            match_query = """
            SELECT range_name, max_amount FROM budget_ranges
            WHERE REPLACE(REPLACE(REPLACE(range_name, '～', '〜'), ' ', ''), '　', '') =
                  REPLACE(REPLACE(REPLACE($1, '～', '〜'), ' ', ''), '　', '')
            """
            match_result = await conn.fetch(match_query, budget)

            if match_result:
                for match in match_result:
                    print(f"     ✅ マッチ: '{match['range_name']}' → max_amount: {match['max_amount']}")
            else:
                print(f"     ❌ マッチなし")

                # 類似検索
                similar_query = "SELECT range_name, max_amount FROM budget_ranges WHERE range_name LIKE '%' || $1 || '%' OR $1 LIKE '%' || range_name || '%'"
                similar_results = await conn.fetch(similar_query, budget)
                if similar_results:
                    print(f"     🔍 類似候補:")
                    for similar in similar_results:
                        print(f"        - '{similar['range_name']}'")

        await conn.close()

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_budget_ranges())