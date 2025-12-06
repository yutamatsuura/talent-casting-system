#!/usr/bin/env python3
"""
budget_rangesテーブルの構造と内容を確認
"""
import asyncio
import asyncpg
import os

async def check_budget_ranges():
    """budget_rangesテーブルの構造と内容を確認"""

    # データベース接続
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URLが設定されていません")
        return

    try:
        conn = await asyncpg.connect(database_url)

        # テーブル構造確認
        print("=== budget_ranges テーブル構造 ===")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'budget_ranges'
            ORDER BY ordinal_position;
        """)

        for col in columns:
            print(f"カラム: {col['column_name']}, 型: {col['data_type']}, NULL許可: {col['is_nullable']}, デフォルト: {col['column_default']}")

        print("\n=== budget_ranges テーブル内容 ===")
        # テーブル内容確認
        rows = await conn.fetch("SELECT * FROM budget_ranges ORDER BY id")

        if rows:
            # カラム名を取得
            column_names = list(rows[0].keys())
            print(f"カラム名: {column_names}")

            print(f"{"ID":>3} | {"名前":<30} | {"最小":>10} | {"最大":>10}")
            print("-" * 60)

            for row in rows:
                # どのカラムが名前かを推測
                name_col = None
                for col in ['name', 'range_name', 'budget_name']:
                    if col in row:
                        name_col = col
                        break

                # どのカラムがmin/maxかを推測
                min_col = None
                max_col = None
                for col in ['min_amount', 'min_budget', 'minimum']:
                    if col in row:
                        min_col = col
                        break

                for col in ['max_amount', 'max_budget', 'maximum']:
                    if col in row:
                        max_col = col
                        break

                id_val = row.get('id', '?')
                name_val = row.get(name_col, '?') if name_col else '?'
                min_val = row.get(min_col, '?') if min_col else '?'
                max_val = row.get(max_col, '?') if max_col else '?'

                print(f"{id_val:>3} | {name_val:<30} | {min_val:>10} | {max_val:>10}")
        else:
            print("データが存在しません")

    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(check_budget_ranges())