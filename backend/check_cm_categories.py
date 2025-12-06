#!/usr/bin/env python3
"""CMカテゴリデータの確認"""
import asyncio
import asyncpg
from app.core.config import settings

async def check_cm_categories():
    """CMカテゴリデータの詳細確認"""
    print("=== CMカテゴリデータ確認 ===")

    conn = await asyncpg.connect(settings.database_url)
    try:
        # m_talent_cmテーブルの構造を確認
        print("\n1. m_talent_cmテーブルの構造:")
        columns_query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'm_talent_cm'
            ORDER BY ordinal_position
        """
        columns = await conn.fetch(columns_query)
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")

        # CMデータのサンプルを取得
        print("\n2. CMデータサンプル（最新10件）:")
        sample_query = """
            SELECT
                account_id,
                client_name,
                product_name,
                use_period_start,
                use_period_end,
                category,
                note
            FROM m_talent_cm
            ORDER BY use_period_end DESC NULLS LAST
            LIMIT 10
        """
        samples = await conn.fetch(sample_query)
        for i, sample in enumerate(samples, 1):
            print(f"  {i}. タレントID: {sample['account_id']}")
            print(f"     クライアント: {sample['client_name']}")
            print(f"     商品: {sample['product_name']}")
            print(f"     期間: {sample['use_period_start']} ～ {sample['use_period_end']}")
            print(f"     カテゴリ: {sample['category']}")
            if sample['note']:
                print(f"     備考: {sample['note']}")
            print()

        # カテゴリの種類を確認
        print("3. カテゴリ一覧:")
        category_query = """
            SELECT
                category,
                COUNT(*) as count
            FROM m_talent_cm
            WHERE category IS NOT NULL AND category != ''
            GROUP BY category
            ORDER BY count DESC
        """
        categories = await conn.fetch(category_query)
        print(f"   総カテゴリ数: {len(categories)}")
        for cat in categories:
            print(f"   - {cat['category']}: {cat['count']}件")

        # 現在CM出演中のタレント（カテゴリ別）
        print("\n4. 現在CM出演中のタレント（カテゴリ別）:")
        current_cm_query = """
            SELECT
                tc.category,
                COUNT(DISTINCT tc.account_id) as talent_count,
                COUNT(*) as cm_count
            FROM m_talent_cm tc
            WHERE tc.use_period_end::date >= CURRENT_DATE
              AND tc.category IS NOT NULL AND tc.category != ''
            GROUP BY tc.category
            ORDER BY talent_count DESC
            LIMIT 20
        """
        current_cms = await conn.fetch(current_cm_query)
        for cm in current_cms:
            print(f"   - {cm['category']}: {cm['talent_count']}名 ({cm['cm_count']}件)")

        # 菓子・氷菓関連のCMを確認
        print("\n5. 菓子・氷菓関連のCM:")
        confectionery_query = """
            SELECT
                tc.account_id,
                ma.name,
                tc.client_name,
                tc.product_name,
                tc.category,
                tc.use_period_start,
                tc.use_period_end,
                CASE
                    WHEN tc.use_period_end::date >= CURRENT_DATE THEN '出演中'
                    ELSE '終了'
                END as status
            FROM m_talent_cm tc
            JOIN m_account ma ON tc.account_id = ma.account_id
            WHERE (
                tc.category ILIKE '%菓子%' OR
                tc.category ILIKE '%お菓子%' OR
                tc.category ILIKE '%スイーツ%' OR
                tc.category ILIKE '%チョコ%' OR
                tc.category ILIKE '%ガム%' OR
                tc.client_name ILIKE '%菓子%' OR
                tc.product_name ILIKE '%菓子%' OR
                tc.product_name ILIKE '%チョコ%' OR
                tc.product_name ILIKE '%ガム%' OR
                tc.product_name ILIKE '%スイーツ%'
            )
            ORDER BY tc.use_period_end DESC NULLS LAST
            LIMIT 15
        """
        confectionery_cms = await conn.fetch(confectionery_query)
        if confectionery_cms:
            for cm in confectionery_cms:
                print(f"   - {cm['name']} | {cm['client_name']} | {cm['product_name']}")
                print(f"     カテゴリ: {cm['category']} | 期間: {cm['use_period_start']} ～ {cm['use_period_end']} | {cm['status']}")
                print()
        else:
            print("   菓子・氷菓関連のCMが見つかりませんでした")

        # 総件数
        print("6. 統計情報:")
        stats_query = """
            SELECT
                COUNT(*) as total_cm_records,
                COUNT(DISTINCT account_id) as total_talents,
                COUNT(CASE WHEN use_period_end::date >= CURRENT_DATE THEN 1 END) as current_cm_count,
                COUNT(DISTINCT CASE WHEN use_period_end::date >= CURRENT_DATE THEN account_id END) as current_cm_talents
            FROM m_talent_cm
        """
        stats = await conn.fetch(stats_query)
        stat = stats[0]
        print(f"   総CM記録数: {stat['total_cm_records']:,}件")
        print(f"   CM経験タレント数: {stat['total_talents']:,}名")
        print(f"   現在CM出演記録数: {stat['current_cm_count']:,}件")
        print(f"   現在CM出演タレント数: {stat['current_cm_talents']:,}名")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_cm_categories())