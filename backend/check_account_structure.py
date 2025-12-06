#!/usr/bin/env python3
"""アカウントテーブルの構造確認"""
import asyncio
import asyncpg
from app.core.config import settings

async def check_account_structure():
    """m_accountテーブルの構造確認"""
    print("=== m_accountテーブル構造確認 ===")

    conn = await asyncpg.connect(settings.database_url)
    try:
        # m_accountテーブルの構造を確認
        print("\n1. m_accountテーブルの構造:")
        columns_query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'm_account'
            ORDER BY ordinal_position
        """
        columns = await conn.fetch(columns_query)
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")

        # サンプルデータ確認
        print("\n2. m_accountサンプルデータ:")
        sample_query = """
            SELECT *
            FROM m_account
            LIMIT 5
        """
        samples = await conn.fetch(sample_query)
        for i, sample in enumerate(samples, 1):
            print(f"  {i}. {dict(sample)}")

        # 特定のタレントIDを確認
        print("\n3. 特定タレントの確認:")
        specific_query = """
            SELECT *
            FROM m_account
            WHERE account_id IN (123, 234, 1111, 30, 1171)
            ORDER BY account_id
        """
        specifics = await conn.fetch(specific_query)
        for talent in specifics:
            print(f"  - ID {talent['account_id']}: {dict(talent)}")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_account_structure())