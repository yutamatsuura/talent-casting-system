#!/usr/bin/env python3
"""
target_segmentsテーブルの内容を確認
"""
import asyncio
import asyncpg
import os

async def check_target_segments():
    """target_segmentsテーブルの内容を確認"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URLが設定されていません")
        return

    try:
        conn = await asyncpg.connect(database_url)

        print("=== target_segments テーブル内容 ===")
        rows = await conn.fetch("SELECT id, name FROM target_segments ORDER BY id")

        if rows:
            print(f"{"ID":>3} | {"ターゲット層名"}")
            print("-" * 40)

            for row in rows:
                id_val = row['id']
                name_val = row['name']
                print(f"{id_val:>3} | {name_val}")
        else:
            print("データが存在しません")

    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(check_target_segments())