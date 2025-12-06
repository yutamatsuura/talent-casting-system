#!/usr/bin/env python3
"""CMデータの詳細確認（修正版）"""
import asyncio
import asyncpg
from app.core.config import settings

async def check_cm_data():
    """CMデータの詳細確認"""
    print("=== CMデータ詳細確認 ===")

    conn = await asyncpg.connect(settings.database_url)
    try:
        # CMデータのサンプルを取得（正しいカラム名で）
        print("\n1. CMデータサンプル（最新10件）:")
        sample_query = """
            SELECT
                account_id,
                sub_id,
                client_name,
                product_name,
                use_period_start,
                use_period_end,
                rival_category_type_cd1,
                rival_category_type_cd2,
                rival_category_type_cd3,
                rival_category_type_cd4,
                agency_name,
                note
            FROM m_talent_cm
            ORDER BY regist_date DESC NULLS LAST
            LIMIT 10
        """
        samples = await conn.fetch(sample_query)
        for i, sample in enumerate(samples, 1):
            print(f"  {i}. タレントID: {sample['account_id']}")
            print(f"     クライアント: {sample['client_name']}")
            print(f"     商品: {sample['product_name']}")
            print(f"     期間: {sample['use_period_start']} ～ {sample['use_period_end']}")
            print(f"     競合カテゴリコード: {sample['rival_category_type_cd1']}, {sample['rival_category_type_cd2']}, {sample['rival_category_type_cd3']}, {sample['rival_category_type_cd4']}")
            print(f"     代理店: {sample['agency_name']}")
            if sample['note']:
                print(f"     備考: {sample['note']}")
            print()

        # 競合カテゴリコードの種類を確認
        print("2. 競合カテゴリコード1の種類:")
        category_query = """
            SELECT
                rival_category_type_cd1,
                COUNT(*) as count
            FROM m_talent_cm
            WHERE rival_category_type_cd1 IS NOT NULL
            GROUP BY rival_category_type_cd1
            ORDER BY count DESC
            LIMIT 20
        """
        categories = await conn.fetch(category_query)
        for cat in categories:
            print(f"   - コード{cat['rival_category_type_cd1']}: {cat['count']}件")

        # 現在CM出演中のタレント数
        print("\n3. 現在CM出演中のタレント:")
        current_cm_query = """
            SELECT
                COUNT(DISTINCT account_id) as current_talent_count,
                COUNT(*) as current_cm_count
            FROM m_talent_cm
            WHERE use_period_end::date >= CURRENT_DATE
        """
        current_stats = await conn.fetch(current_cm_query)
        stat = current_stats[0]
        print(f"   現在CM出演中タレント数: {stat['current_talent_count']}名")
        print(f"   現在CM出演中CM件数: {stat['current_cm_count']}件")

        # 菓子・氷菓関連のCMを商品名・クライアント名から検索
        print("\n4. 菓子・氷菓関連のCM検索:")
        confectionery_query = """
            SELECT
                tc.account_id,
                ma.name,
                tc.client_name,
                tc.product_name,
                tc.use_period_start,
                tc.use_period_end,
                tc.rival_category_type_cd1,
                CASE
                    WHEN tc.use_period_end::date >= CURRENT_DATE THEN '出演中'
                    ELSE '終了'
                END as status
            FROM m_talent_cm tc
            JOIN m_account ma ON tc.account_id = ma.account_id
            WHERE (
                tc.client_name ILIKE '%菓子%' OR
                tc.client_name ILIKE '%製菓%' OR
                tc.client_name ILIKE '%お菓子%' OR
                tc.product_name ILIKE '%菓子%' OR
                tc.product_name ILIKE '%チョコ%' OR
                tc.product_name ILIKE '%ガム%' OR
                tc.product_name ILIKE '%スイーツ%' OR
                tc.product_name ILIKE '%クッキー%' OR
                tc.product_name ILIKE '%ケーキ%' OR
                tc.product_name ILIKE '%飴%'
            )
            ORDER BY tc.use_period_end DESC NULLS LAST
            LIMIT 15
        """
        confectionery_cms = await conn.fetch(confectionery_query)
        if confectionery_cms:
            for cm in confectionery_cms:
                print(f"   - {cm['name']} | {cm['client_name']} | {cm['product_name']}")
                print(f"     カテゴリコード: {cm['rival_category_type_cd1']} | 期間: {cm['use_period_start']} ～ {cm['use_period_end']} | {cm['status']}")
                print()
        else:
            print("   菓子・氷菓関連のCMが見つかりませんでした")

        # マスターテーブルがあるかチェック
        print("\n5. カテゴリマスターテーブルの確認:")
        master_tables_query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND (table_name ILIKE '%category%' OR table_name ILIKE '%rival%')
        """
        master_tables = await conn.fetch(master_tables_query)
        if master_tables:
            for table in master_tables:
                print(f"   - {table['table_name']}")
        else:
            print("   カテゴリ関連のマスターテーブルが見つかりませんでした")

        # 実際にAPIで使われているタレントのCM状況を確認
        print("\n6. 菓子・氷菓業界診断で上位に来るタレントのCM状況:")
        talent_cm_check_query = """
            SELECT
                ma.account_id,
                ma.name,
                COUNT(tc.account_id) as total_cm_count,
                COUNT(CASE WHEN tc.use_period_end::date >= CURRENT_DATE THEN 1 END) as current_cm_count,
                MAX(CASE WHEN tc.use_period_end::date >= CURRENT_DATE THEN tc.use_period_end END) as latest_current_end
            FROM m_account ma
            LEFT JOIN m_talent_cm tc ON ma.account_id = tc.account_id
            WHERE ma.account_id IN (123, 234, 1111, 30, 1171, 651, 618, 1214, 1342, 920)  -- APIテスト結果の上位タレント
            GROUP BY ma.account_id, ma.name
            ORDER BY ma.account_id
        """
        talent_cms = await conn.fetch(talent_cm_check_query)
        for talent in talent_cms:
            status = "出演中" if talent['current_cm_count'] > 0 else "未出演"
            print(f"   - {talent['name']} (ID: {talent['account_id']}): 総CM{talent['total_cm_count']}件, 現在{talent['current_cm_count']}件 | {status}")
            if talent['latest_current_end']:
                print(f"     最新CM終了予定: {talent['latest_current_end']}")

        # 統計情報
        print("\n7. 統計情報:")
        stats_query = """
            SELECT
                COUNT(*) as total_cm_records,
                COUNT(DISTINCT account_id) as total_talents,
                COUNT(CASE WHEN use_period_end::date >= CURRENT_DATE THEN 1 END) as current_cm_count,
                COUNT(DISTINCT CASE WHEN use_period_end::date >= CURRENT_DATE THEN account_id END) as current_cm_talents,
                MIN(use_period_start) as oldest_start,
                MAX(use_period_end) as latest_end
            FROM m_talent_cm
        """
        stats = await conn.fetch(stats_query)
        stat = stats[0]
        print(f"   総CM記録数: {stat['total_cm_records']:,}件")
        print(f"   CM経験タレント数: {stat['total_talents']:,}名")
        print(f"   現在CM出演記録数: {stat['current_cm_count']:,}件")
        print(f"   現在CM出演タレント数: {stat['current_cm_talents']:,}名")
        print(f"   データ期間: {stat['oldest_start']} ～ {stat['latest_end']}")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_cm_data())