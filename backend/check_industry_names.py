#!/usr/bin/env python3
"""業種名の確認スクリプト"""
import asyncio
from app.db.connection import get_asyncpg_connection

async def check_industry_names():
    """実際の業種名をチェック"""
    conn = await get_asyncpg_connection()
    try:
        result = await conn.fetch("SELECT DISTINCT industry_name FROM industries ORDER BY industry_name")
        print("📋 データベース内の業種名一覧:")
        for i, row in enumerate(result, 1):
            print(f"   {i:2d}. {row['industry_name']}")

        print(f"\n合計: {len(result)}件")

        # 食品関連を検索
        food_related = await conn.fetch(
            "SELECT industry_name FROM industries WHERE industry_name LIKE '%食品%' OR industry_name LIKE '%飲料%' ORDER BY industry_name"
        )
        if food_related:
            print("\n🍽️ 食品・飲料関連の業種:")
            for row in food_related:
                print(f"   - {row['industry_name']}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_industry_names())