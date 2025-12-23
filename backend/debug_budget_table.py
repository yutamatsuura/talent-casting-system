#!/usr/bin/env python3
"""
budget_rangesテーブルの内容を確認
"""
import asyncio
from app.db.connection import get_asyncpg_connection, release_asyncpg_connection

async def debug_budget_table():
    """budget_rangesテーブルの内容をデバッグ"""
    print("=" * 80)
    print("🔍 budget_rangesテーブルデバッグ")
    print("=" * 80)

    conn = await get_asyncpg_connection()
    try:
        # budget_rangesテーブルの全内容を確認
        rows = await conn.fetch("SELECT * FROM budget_ranges ORDER BY max_amount")

        print(f"budget_ranges テーブル内容 ({len(rows)}件):")
        for row in rows:
            print(f"  range_name: {row['range_name']}")
            print(f"  max_amount: {row['max_amount']}")
            print(f"  ---")

        print("\n「1,000万円未満」の検索:")
        target_budget = "1,000万円未満"

        # 文字列正規化
        from app.api.endpoints.matching import normalize_budget_range_string
        normalized = normalize_budget_range_string(target_budget)
        print(f"  元の文字列: '{target_budget}'")
        print(f"  正規化後: '{normalized}'")

        # 直接検索
        result = await conn.fetchrow(
            "SELECT * FROM budget_ranges WHERE REPLACE(REPLACE(REPLACE(range_name, '～', '〜'), ' ', ''), '　', '') = $1",
            normalized
        )

        if result:
            print(f"  検索結果:")
            print(f"    range_name: {result['range_name']}")
            print(f"    max_amount: {result['max_amount']}")
        else:
            print("  検索結果: 見つかりません")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await release_asyncpg_connection(conn)

if __name__ == "__main__":
    asyncio.run(debug_budget_table())