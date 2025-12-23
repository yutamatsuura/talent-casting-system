import asyncio
import os
import sys
sys.path.append('/Users/lennon/projects/talent-casting-form/backend')

from app.db.connection import get_db_connection

async def debug_budget_data():
    """予算データの詳細分析"""
    try:
        conn = await get_db_connection()
        
        print("=== 予算データサンプル調査 ===")
        
        # 予算データのサンプルを取得
        query = """
        SELECT 
            ma.account_id,
            ma.name,
            mta.money_min_one_year,
            mta.money_max_one_year,
            -- 修正後の計算結果
            mta.money_min_one_year * 10000 as min_yen,
            mta.money_max_one_year * 10000 as max_yen
        FROM master_talents_money_annual mta
        JOIN master_talents ma ON mta.account_id = ma.account_id
        WHERE mta.money_min_one_year IS NOT NULL
        ORDER BY mta.money_min_one_year ASC
        LIMIT 10
        """
        
        rows = await conn.fetch(query)
        
        print(f"予算データサンプル（最低価格順）:")
        for row in rows:
            print(f"  {row['name']}: MIN={row['money_min_one_year']:,}万円({row['min_yen']:,}円), MAX={row['money_max_one_year']}")
        
        # 3,000万円以下のタレント数をチェック
        print("\n=== 予算範囲別のタレント数 ===")
        budget_ranges = [
            (0, 1000),      # 1,000万円以下
            (0, 3000),      # 3,000万円以下  
            (0, 5000),      # 5,000万円以下
            (0, 10000),     # 1億円以下
        ]
        
        for min_budget, max_budget in budget_ranges:
            count_query = """
            SELECT COUNT(*) as count
            FROM master_talents_money_annual mta
            JOIN master_talents ma ON mta.account_id = ma.account_id
            WHERE mta.money_min_one_year IS NOT NULL
            AND mta.money_min_one_year * 10000 <= %s
            """
            max_yen = max_budget * 10000000  # 万円を円に変換
            count_result = await conn.fetchrow(count_query, max_yen)
            print(f"  {max_budget:,}万円以下: {count_result['count']}人")
        
        await conn.close()
        
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    asyncio.run(debug_budget_data())
