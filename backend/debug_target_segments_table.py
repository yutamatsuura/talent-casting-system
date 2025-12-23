#!/usr/bin/env python3
"""
target_segmentsテーブル構造確認
"""
import asyncio
import asyncpg

async def check_target_segments_table():
    """target_segmentsテーブル構造確認"""
    try:
        conn = await asyncpg.connect(
            host='ep-sparkling-smoke-a183z7h8-pooler.ap-southeast-1.aws.neon.tech',
            user='neondb_owner',
            password='npg_5X1MlRZzVheF',
            database='neondb',
            ssl='require'
        )

        # テーブル構造確認
        schema_query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'target_segments'
        ORDER BY ordinal_position
        """
        schema_rows = await conn.fetch(schema_query)

        print("📋 target_segmentsテーブル構造:")
        for row in schema_rows:
            print(f"   {row['column_name']}: {row['data_type']}")

        # データサンプル確認
        print(f"\n📊 target_segmentsテーブル内容:")
        data_query = "SELECT * FROM target_segments LIMIT 5"
        data_rows = await conn.fetch(data_query)

        for row in data_rows:
            print(f"   {dict(row)}")

        await conn.close()

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_target_segments_table())