import asyncio
import asyncpg

async def check_aragaki_data():
    DATABASE_URL = "postgresql://neondb_owner:npg_5X1MlRZzVheF@ep-sparkling-smoke-a183z7h8-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    # まず、新垣結衣のtalent_idを確認
    query1 = """
    SELECT id, name FROM talent WHERE name = '新垣結衣'
    """
    talent_result = await conn.fetchrow(query1)
    
    if talent_result:
        talent_id = talent_result['id']
        print(f"=== 新垣結衣 (ID: {talent_id}) のデータ ===")
        
        # money_talent_amountsテーブルから予算データを取得
        query2 = """
        SELECT money_min_one_year, money_max_one_year
        FROM money_talent_amounts 
        WHERE talent_id = $1
        """
        money_result = await conn.fetchrow(query2, talent_id)
        
        if money_result:
            print(f"最低出演料: {money_result['money_min_one_year']:,}万円")
            print(f"最高出演料: {money_result['money_max_one_year']:,}万円")
        else:
            print("予算データが見つかりません")
            
        # テストするユーザーの予算条件
        test_budget = "1,000万円～3,000万円未満"
        print(f"\nテスト予算条件: {test_budget}")
        
        # 予算範囲の上限値 (3,000万円)
        budget_upper = 3000
        min_fee = money_result['money_min_one_year'] if money_result else None
        
        if min_fee:
            print(f"予算上限 {budget_upper}万円 vs 最低出演料 {min_fee}万円")
            if min_fee <= budget_upper:
                print("→ 条件クリア: 表示される (バグ！)")
            else:
                print("→ 条件外: 除外される (正常)")
    else:
        print("新垣結衣が見つかりません")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_aragaki_data())
