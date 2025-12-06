#!/usr/bin/env python3
"""talentsテーブルの構造を確認"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv('/Users/lennon/projects/talent-casting-form/.env.local')

async def check_talents_schema():
    """talentsテーブルの構造を詳細確認"""
    database_url = os.getenv('DATABASE_URL')

    try:
        conn = await asyncpg.connect(database_url)
        print("✅ データベース接続成功")

        # talents テーブル構造確認
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'talents'
            ORDER BY ordinal_position
        """)

        print("\n📋 talents テーブル構造:")
        for col in columns:
            nullable = "NULL可" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f"デフォルト: {col['column_default']}" if col['column_default'] else "デフォルトなし"
            print(f"  - {col['column_name']}: {col['data_type']} ({nullable}, {default})")

        # 他の関連テーブルの構造も確認
        tables = ["talent_scores", "talent_images"]
        for table in tables:
            columns = await conn.fetch(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table}'
                ORDER BY ordinal_position
            """)

            print(f"\n📋 {table} テーブル構造:")
            for col in columns:
                nullable = "NULL可" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"  - {col['column_name']}: {col['data_type']} ({nullable})")

        await conn.close()

    except Exception as e:
        print(f"❌ エラー発生: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_talents_schema())