#!/usr/bin/env python3
"""
予算区分の正確な名前を確認
"""
import asyncio
from app.db.connection import get_asyncpg_connection

async def check_budget_ranges():
    conn = await get_asyncpg_connection()
    try:
        query = "SELECT range_name, max_amount FROM budget_ranges ORDER BY max_amount"
        rows = await conn.fetch(query)

        print("予算区分名一覧:")
        for row in rows:
            print(f"  '{row['range_name']}' -> {row['max_amount']}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_budget_ranges())