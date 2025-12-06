#!/usr/bin/env python3
"""
STEP 0予算フィルタリングの詳細デバッグ
"""
import asyncio
import asyncpg
import os

async def debug_step0_filtering():
    """STEP 0予算フィルタリングの詳細デバッグ"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URLが設定されていません")
        return

    try:
        conn = await asyncpg.connect(database_url)

        # 1. 予算範囲「1,000万円未満」のmin_amount, max_amountを確認
        print("=== 1. 予算範囲「1,000万円未満」の設定 ===")
        budget_row = await conn.fetchrow(
            "SELECT min_amount, max_amount FROM budget_ranges WHERE name = $1",
            "1,000万円未満"
        )
        if budget_row:
            min_budget = float(budget_row["min_amount"] or 0)
            max_budget = float(budget_row["max_amount"] or float("inf"))
            print(f"min_budget: {min_budget}")
            print(f"max_budget: {max_budget}")
        else:
            print("予算範囲が見つかりません")
            return

        # 2. talentsテーブルの予算データ統計
        print("\n=== 2. talentsテーブルの予算データ統計 ===")
        stats = await conn.fetchrow("""
            SELECT
                COUNT(*) as total_talents,
                COUNT(money_max_one_year) as with_budget,
                COUNT(*) - COUNT(money_max_one_year) as null_budget,
                MIN(money_max_one_year) as min_budget_value,
                MAX(money_max_one_year) as max_budget_value
            FROM talents
        """)

        for key, value in stats.items():
            print(f"{key}: {value}")

        # 3. STEP 0フィルタリングの各条件別タレント数
        print("\n=== 3. STEP 0フィルタリング条件別タレント数 ===")

        # ①NULL条件
        null_count = await conn.fetchval("SELECT COUNT(*) FROM talents WHERE money_max_one_year IS NULL")
        print(f"①NULLタレント: {null_count}人")

        # ②min_budget条件（min_budget=0の場合）
        if min_budget == 0:
            min_condition_count = await conn.fetchval("SELECT COUNT(*) FROM talents WHERE money_max_one_year >= 0 OR 0 = 0")
            print(f"②min_budget=0条件: {min_condition_count}人（実質全タレント）")
        else:
            min_condition_count = await conn.fetchval("SELECT COUNT(*) FROM talents WHERE money_max_one_year >= $1", min_budget)
            print(f"②money_max_one_year >= {min_budget}: {min_condition_count}人")

        # ③max_budget条件
        if max_budget == float("inf"):
            max_condition_count = await conn.fetchval("SELECT COUNT(*) FROM talents WHERE money_max_one_year <= $1 OR $1 = 'Infinity'::float8", max_budget)
            print(f"③max_budget=∞条件: {max_condition_count}人（実質全タレント）")
        else:
            max_condition_count = await conn.fetchval("SELECT COUNT(*) FROM talents WHERE money_max_one_year <= $1", max_budget)
            print(f"③money_max_one_year <= {max_budget}: {max_condition_count}人")

        # 4. 完全なSTEP 0フィルタリング結果
        print("\n=== 4. 完全なSTEP 0フィルタリング結果 ===")
        step0_query = """
        SELECT COUNT(*) FROM talents t
        WHERE (
            t.money_max_one_year IS NULL
            OR (
                (t.money_max_one_year >= $1 OR $1 = 0)
                AND (t.money_max_one_year <= $2 OR $2 = 'Infinity'::float8)
            )
        )
        """

        step0_count = await conn.fetchval(step0_query, min_budget, max_budget)
        print(f"STEP 0フィルタリング結果: {step0_count}人")

        # 5. 予算範囲内のタレント（NULLを除く）
        print("\n=== 5. 予算範囲内のタレント（NULLを除く）===")
        budget_range_query = """
        SELECT COUNT(*) FROM talents t
        WHERE t.money_max_one_year IS NOT NULL
          AND t.money_max_one_year >= $1
          AND t.money_max_one_year <= $2
        """

        in_range_count = await conn.fetchval(budget_range_query, min_budget, max_budget)
        print(f"予算範囲内（{min_budget}～{max_budget}万円）: {in_range_count}人")

        # サンプル表示
        sample_query = """
        SELECT name, money_max_one_year FROM talents t
        WHERE t.money_max_one_year IS NOT NULL
          AND t.money_max_one_year >= $1
          AND t.money_max_one_year <= $2
        ORDER BY money_max_one_year
        LIMIT 5
        """

        samples = await conn.fetch(sample_query, min_budget, max_budget)
        print("サンプル:")
        for sample in samples:
            print(f"  {sample['name']}: {sample['money_max_one_year']}万円")

    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(debug_step0_filtering())