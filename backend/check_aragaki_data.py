import asyncio
import asyncpg
import os

async def check_aragaki_data():
    # データベース接続
    DATABASE_URL = "postgresql://neondb_owner:npg_5X1MlRZzVheF@ep-sparkling-smoke-a183z7h8-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    # 新垣結衣のデータを確認
    query = """
    SELECT 
        t.id, 
        t.name, 
        mta.money_min_one_year,
        mta.money_max_one_year
    FROM talents t
    LEFT JOIN money_talent_amounts mta ON t.id = mta.talent_id
    WHERE t.name = '新垣結衣'
    """
    
    result = await conn.fetchrow(query)
    
    print("=== 新垣結衣のデータベース情報 ===")
    if result:
        print(f"ID: {result['id']}")
        print(f"名前: {result['name']}")
        print(f"最低出演料: {result['money_min_one_year']:,}万円" if result['money_min_one_year'] else "最低出演料: なし")
        print(f"最高出演料: {result['money_max_one_year']:,}万円" if result['money_max_one_year'] else "最高出演料: なし")
    else:
        print("新垣結衣のデータが見つかりません")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_aragaki_data())
