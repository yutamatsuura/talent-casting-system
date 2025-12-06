#!/usr/bin/env python3
"""データベーステーブル構造確認スクリプト"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.connection import get_asyncpg_connection

async def check_table_structures():
    """テーブル構造の確認"""

    try:
        conn = await get_asyncpg_connection()

        # industries テーブルの構造確認
        print("📋 industries テーブル構造:")
        industries_sql = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'industries'
            ORDER BY ordinal_position;
        """

        industries_columns = await conn.fetch(industries_sql)
        if industries_columns:
            for col in industries_columns:
                nullable = "NULL" if col['is_nullable'] == "YES" else "NOT NULL"
                print(f"  - {col['column_name']}: {col['data_type']} ({nullable})")
        else:
            print("  ❌ industries テーブルが見つかりません")

        print()

        # m_account テーブルの構造確認
        print("📋 m_account テーブル構造:")
        m_account_sql = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'm_account'
            ORDER BY ordinal_position;
        """

        m_account_columns = await conn.fetch(m_account_sql)
        if m_account_columns:
            for col in m_account_columns:
                nullable = "NULL" if col['is_nullable'] == "YES" else "NOT NULL"
                print(f"  - {col['column_name']}: {col['data_type']} ({nullable})")
        else:
            print("  ❌ m_account テーブルが見つかりません")

        print()

        # 既存のテーブル一覧
        print("📋 既存テーブル一覧:")
        tables_sql = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """

        tables = await conn.fetch(tables_sql)
        for table in tables:
            print(f"  - {table['table_name']}")

    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(check_table_structures())