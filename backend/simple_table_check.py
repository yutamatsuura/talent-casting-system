#!/usr/bin/env python3
"""
実際のテーブル構造確認
"""
import asyncio
from app.db.connection import get_asyncpg_connection

async def check_tables():
    conn = await get_asyncpg_connection()
    try:
        # 全テーブル一覧取得
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        print("📋 実際のデータベーステーブル一覧:")
        for table in tables:
            print(f"   - {table['table_name']}")

        # 重要なテーブルの詳細確認
        important_tables = ['m_account', 'm_talent_act', 'talent_scores', 'talent_images',
                           'industries', 'target_segments', 'budget_ranges']

        for table_name in important_tables:
            try:
                columns = await conn.fetch(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """)

                if columns:
                    print(f"\n📊 {table_name}テーブル構造:")
                    for col in columns:
                        print(f"     {col['column_name']} ({col['data_type']}, nullable: {col['is_nullable']})")
                else:
                    print(f"\n❌ {table_name}テーブル: 存在しない")
            except Exception as e:
                print(f"\n❌ {table_name}テーブル: エラー - {e}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_tables())