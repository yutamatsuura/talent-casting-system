#!/usr/bin/env python3
"""
テーブル構造確認スクリプト
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    try:
        # データベースに接続
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            db_url = "postgresql://neondb_owner:npg_5X1MlRZzVheF@ep-sparkling-smoke-a183z7h8-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

        conn = await asyncpg.connect(db_url)

        # form_submissionsテーブルの構造を確認
        query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'form_submissions'
        ORDER BY ordinal_position;
        """

        results = await conn.fetch(query)

        print("📊 form_submissionsテーブル構造:")
        for row in results:
            print(f"   {row['column_name']}: {row['data_type']}")

        # 実際のデータを1件確認
        data_query = "SELECT * FROM form_submissions LIMIT 1"
        data_results = await conn.fetch(data_query)

        if data_results:
            print(f"\n📋 サンプルデータ (ID: {data_results[0]['id']}):")
            for key, value in dict(data_results[0]).items():
                print(f"   {key}: {value}")
        else:
            print("\n📋 データが存在しません")

        await conn.close()

    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    asyncio.run(main())