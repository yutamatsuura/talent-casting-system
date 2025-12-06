#!/usr/bin/env python3
"""Phase B パラメータ取得デバッグスクリプト"""
import asyncio
from app.db.connection import get_asyncpg_connection

async def debug_parameter_query():
    """パラメータクエリの各段階を個別にデバッグ"""

    # テストパラメータ
    budget_range = "1,000万円〜3,000万円未満"
    target_segment_name = "女性35-49歳"
    industry_name = "食品・飲料・酒類"

    print("=" * 80)
    print("🔍 Phase B パラメータ取得デバッグ")
    print("=" * 80)
    print(f"予算区分: {budget_range}")
    print(f"ターゲット層: {target_segment_name}")
    print(f"業種: {industry_name}")

    conn = await get_asyncpg_connection()
    try:
        # 1. budget_ranges テーブルチェック
        print("\n1. 予算区分テーブル確認:")
        budget_query = """
        SELECT range_name, max_amount
        FROM budget_ranges
        WHERE REPLACE(REPLACE(REPLACE(range_name, '～', '〜'), ' ', ''), '　', '') =
              REPLACE(REPLACE(REPLACE($1, '～', '〜'), ' ', ''), '　', '')
        """
        budget_result = await conn.fetchrow(budget_query, budget_range)
        print(f"   結果: {budget_result}")

        # 2. target_segments テーブルチェック
        print("\n2. ターゲット層テーブル確認:")
        segment_query = "SELECT target_segment_id, segment_name FROM target_segments WHERE segment_name = $1"
        segment_result = await conn.fetchrow(segment_query, target_segment_name)
        print(f"   結果: {segment_result}")

        # 3. industries テーブルチェック
        print("\n3. 業種テーブル確認:")
        industry_query = """
        SELECT industry_name, required_image_id,
               CASE WHEN industry_name = 'アルコール飲料' THEN true ELSE false END as is_alcohol
        FROM industries WHERE industry_name = $1
        """
        industry_result = await conn.fetchrow(industry_query, industry_name)
        print(f"   結果: {industry_result}")

        # 4. 統合クエリテスト
        print("\n4. 統合パラメータクエリテスト:")
        params_query = """
        WITH budget_info AS (
            SELECT max_amount FROM budget_ranges
            WHERE REPLACE(REPLACE(REPLACE(range_name, '～', '〜'), ' ', ''), '　', '') =
                  REPLACE(REPLACE(REPLACE($1, '～', '〜'), ' ', ''), '　', '')
        ),
        segment_info AS (
            SELECT target_segment_id FROM target_segments WHERE segment_name = $2
        ),
        image_info AS (
            SELECT
                CASE
                    WHEN i.required_image_id IS NOT NULL THEN ARRAY[i.required_image_id]
                    ELSE ARRAY[1,2,3,4,5,6,7]
                END as image_item_ids,
                CASE WHEN i.industry_name = 'アルコール飲料' THEN true ELSE false END as is_alcohol
            FROM industries i WHERE i.industry_name = $3
        )
        SELECT
            COALESCE(bi.max_amount, 'Infinity'::float8) as budget_max,
            si.target_segment_id,
            ii.image_item_ids,
            ii.is_alcohol
        FROM budget_info bi
        CROSS JOIN segment_info si
        CROSS JOIN image_info ii
        """

        params_result = await conn.fetchrow(params_query, budget_range, target_segment_name, industry_name)
        print(f"   結果: {params_result}")

        if not params_result:
            print("\n❌ 統合クエリが結果を返しませんでした")

            # 各CTEを個別確認
            print("\n5. 個別CTE確認:")

            budget_cte = await conn.fetchrow(
                "SELECT max_amount FROM budget_ranges WHERE REPLACE(REPLACE(REPLACE(range_name, '～', '〜'), ' ', ''), '　', '') = REPLACE(REPLACE(REPLACE($1, '～', '〜'), ' ', ''), '　', '')",
                budget_range
            )
            print(f"   budget_info: {budget_cte}")

            segment_cte = await conn.fetchrow(
                "SELECT target_segment_id FROM target_segments WHERE segment_name = $1",
                target_segment_name
            )
            print(f"   segment_info: {segment_cte}")

            image_cte = await conn.fetchrow(
                "SELECT CASE WHEN i.required_image_id IS NOT NULL THEN ARRAY[i.required_image_id] ELSE ARRAY[1,2,3,4,5,6,7] END as image_item_ids, CASE WHEN i.industry_name = 'アルコール飲料' THEN true ELSE false END as is_alcohol FROM industries i WHERE i.industry_name = $1",
                industry_name
            )
            print(f"   image_info: {image_cte}")
        else:
            print("\n✅ 統合クエリ成功")
            print(f"   budget_max: {params_result['budget_max']}")
            print(f"   target_segment_id: {params_result['target_segment_id']}")
            print(f"   image_item_ids: {params_result['image_item_ids']}")
            print(f"   is_alcohol: {params_result['is_alcohol']}")

    except Exception as e:
        print(f"\n❌ エラー: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(debug_parameter_query())