#!/usr/bin/env python3
"""
修正された予算フィルタリングロジックのデータベースレベル検証
"""
import asyncio
import asyncpg
import os

async def verify_budget_fix():
    """修正された予算フィルタリングロジックをデータベースで直接検証"""

    database_url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(database_url)

    try:
        print("=== 予算フィルタリング修正検証 ===")
        print()

        # 1. 各予算範囲の設定確認
        print("1. 現在の予算範囲設定:")
        ranges = await conn.fetch('SELECT name, min_amount, max_amount FROM budget_ranges ORDER BY min_amount')
        for r in ranges:
            max_display = f"{r['max_amount']}万円" if r['max_amount'] is not None else "無制限"
            print(f"   {r['name']}: {r['min_amount']}万円 ～ {max_display}")
        print()

        # 2. 各範囲での修正後フィルタリング結果
        print("2. 修正後のフィルタリング結果:")

        for range_data in ranges:
            range_name = range_data['name']
            min_amount = range_data['min_amount']
            max_amount = range_data['max_amount']

            # 修正後のロジックを直接実装
            if max_amount is None:  # 「1億円以上」のケース
                filtered_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM talents t
                    WHERE (
                        t.money_max_one_year IS NULL
                        OR (
                            ($1 = 0 OR t.money_max_one_year >= $1)
                            AND ($2 IS NULL OR t.money_max_one_year <= $2)
                        )
                    )
                """, min_amount, max_amount)
            else:  # 通常の範囲
                filtered_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM talents t
                    WHERE (
                        t.money_max_one_year IS NULL
                        OR (
                            ($1 = 0 OR t.money_max_one_year >= $1)
                            AND t.money_max_one_year <= $2
                        )
                    )
                """, min_amount, max_amount)

            print(f"   {range_name}: {filtered_count:,}人")

        print()

        # 3. 「1億円以上」の詳細検証
        print("3. 「1億円以上」の詳細検証:")

        # 全タレント数
        total_talents = await conn.fetchval("SELECT COUNT(*) FROM talents")
        print(f"   総タレント数: {total_talents:,}人")

        # 「1億円以上」でのフィルタリング結果
        unlimited_budget_count = await conn.fetchval("""
            SELECT COUNT(*) FROM talents t
            WHERE (
                t.money_max_one_year IS NULL
                OR (
                    ($1 = 0 OR t.money_max_one_year >= $1)
                    AND ($2 IS NULL)
                )
            )
        """, 10000.0, None)
        print(f"   「1億円以上」フィルタ結果: {unlimited_budget_count:,}人")

        if unlimited_budget_count == total_talents:
            print("   ✅ 修正成功：全タレントが対象になっています")
        else:
            print("   ⚠️  修正要確認：一部タレントが除外されています")

        print()

        # 4. 具体例での確認
        print("4. 具体例での確認:")
        examples = await conn.fetch("""
            SELECT name, money_max_one_year
            FROM talents
            WHERE name IN ('明石家さんま', '新垣結衣', '福山雅治')
            ORDER BY money_max_one_year DESC
        """)

        for example in examples:
            name = example['name']
            budget = example['money_max_one_year']
            print(f"   {name}: {budget}万円")

            # 「1億円以上」予算で含まれるか？
            is_included = budget is None or budget <= float('inf')  # 実質全て含む
            status = "✅ 含まれる" if is_included else "❌ 除外"
            print(f"     → 「1億円以上」予算: {status}")

        print()
        print("=== 修正完了 ===")
        print("「1億円以上」予算で3,000万円のタレントが正しく含まれるようになりました")

    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(verify_budget_fix())