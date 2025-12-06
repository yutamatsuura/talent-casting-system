#!/usr/bin/env python3
"""
予算フィルタリングロジックの問題分析
"""
import asyncio
import asyncpg
import os

async def analyze_budget_logic():
    """予算フィルタリングロジックの問題を具体例で分析"""

    database_url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(database_url)

    try:
        print("=== 予算フィルタリング仕様問題の分析 ===")
        print()

        # 1. 現在の予算範囲
        print("1. 現在の予算範囲設定:")
        ranges = await conn.fetch('SELECT name, min_amount, max_amount FROM budget_ranges ORDER BY min_amount')
        for r in ranges:
            max_display = f"{r['max_amount']}万円" if r['max_amount'] is not None else "無制限"
            print(f"   {r['name']}: {r['min_amount']}万円 ～ {max_display}")
        print()

        # 2. タレント予算分布（簡易版）
        print("2. タレント予算分布:")
        stats = await conn.fetch("""
            SELECT
                COUNT(CASE WHEN money_max_one_year IS NULL THEN 1 END) as null_count,
                COUNT(CASE WHEN money_max_one_year < 1000 THEN 1 END) as under_1000,
                COUNT(CASE WHEN money_max_one_year BETWEEN 1000 AND 2999 THEN 1 END) as range_1000_3000,
                COUNT(CASE WHEN money_max_one_year BETWEEN 3000 AND 9999 THEN 1 END) as range_3000_10000,
                COUNT(CASE WHEN money_max_one_year >= 10000 THEN 1 END) as over_10000
            FROM talents
        """)

        stat = stats[0]
        print(f"   NULL（予算不明）: {stat['null_count']:,}人")
        print(f"   1,000万円未満: {stat['under_1000']:,}人")
        print(f"   1,000万円-2,999万円: {stat['range_1000_3000']:,}人")
        print(f"   3,000万円-9,999万円: {stat['range_3000_10000']:,}人")
        print(f"   1億円以上: {stat['over_10000']:,}人")
        print()

        # 3. 問題のケース：「1億円以上」予算での現在のフィルタ結果
        print("3. 問題ケース分析：クライアント予算「1億円以上」")
        print("   現在のロジック（問題あり）:")

        current_logic_result = await conn.fetchval("""
            SELECT COUNT(*) FROM talents t
            WHERE (
                t.money_max_one_year IS NULL
                OR (
                    (t.money_max_one_year >= 10000 OR 10000 = 0)
                    AND (t.money_max_one_year <= 'Infinity'::float8 OR 'Infinity'::float8 = 'Infinity'::float8)
                )
            )
        """)

        print(f"   → フィルタ通過: {current_logic_result:,}人")

        # この内訳
        null_talents = await conn.fetchval("SELECT COUNT(*) FROM talents WHERE money_max_one_year IS NULL")
        over_10000_talents = await conn.fetchval("SELECT COUNT(*) FROM talents WHERE money_max_one_year >= 10000")

        print(f"     - 予算不明: {null_talents:,}人")
        print(f"     - 1億円以上のタレント: {over_10000_talents:,}人")
        print()

        # 4. 正しいロジックでの結果
        print("   正しいロジック（修正案）:")

        correct_logic_result = await conn.fetchval("""
            SELECT COUNT(*) FROM talents t
            WHERE (
                t.money_max_one_year IS NULL
                OR t.money_max_one_year <= 'Infinity'::float8
            )
        """)

        print(f"   → フィルタ通過: {correct_logic_result:,}人（実質全タレント）")
        print()

        # 5. 実用的な上限設定の提案
        print("4. 実用的な修正案:")
        print("   「1億円以上」は実質無制限として、全タレント（NULL含む）を対象とする")
        print("   または、現実的な上限（例：5億円）を設定する")
        print()

        # 6. 各予算範囲での修正前後の比較
        print("5. 修正前後の比較（各予算範囲）:")

        for r in ranges:
            range_name = r['name']
            min_amount = r['min_amount']
            max_amount = r['max_amount'] if r['max_amount'] is not None else float('inf')

            # 現在のロジック
            if max_amount == float('inf'):
                current_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM talents t
                    WHERE (
                        t.money_max_one_year IS NULL
                        OR (
                            (t.money_max_one_year >= $1)
                            AND (t.money_max_one_year <= 'Infinity'::float8 OR 'Infinity'::float8 = 'Infinity'::float8)
                        )
                    )
                """, min_amount)
            else:
                current_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM talents t
                    WHERE (
                        t.money_max_one_year IS NULL
                        OR (
                            t.money_max_one_year >= $1
                            AND t.money_max_one_year <= $2
                        )
                    )
                """, min_amount, max_amount)

            # 修正後のロジック
            if max_amount == float('inf'):
                correct_count = await conn.fetchval("SELECT COUNT(*) FROM talents")
            else:
                correct_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM talents t
                    WHERE (
                        t.money_max_one_year IS NULL
                        OR t.money_max_one_year <= $1
                    )
                """, max_amount)

            print(f"   {range_name}:")
            print(f"     現在: {current_count:,}人 → 修正後: {correct_count:,}人")

        print()
        print("=== 結論 ===")
        print("ユーザーのご指摘は100%正しいです。")
        print("現在のロジックはビジネス要件と乖離しており、修正が必要です。")

    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(analyze_budget_logic())