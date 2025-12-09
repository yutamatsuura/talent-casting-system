import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.db.connection import get_asyncpg_connection

async def main():
    conn = await get_asyncpg_connection()
    rows = await conn.fetch('SELECT segment_name FROM target_segments ORDER BY target_segment_id LIMIT 10')
    print('\n'.join([r['segment_name'] for r in rows]))
    await conn.close()

asyncio.run(main())
