#!/usr/bin/env python3
"""CMカテゴリデータの最終確認"""
import asyncio
import asyncpg
from app.core.config import settings

async def check_cm_final():
    """CMカテゴリデータの最終確認"""
    print("=== CMカテゴリデータ最終確認 ===")

    conn = await asyncpg.connect(settings.database_url)
    try:
        print("\n📊 重要な統計情報:")
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
        print(f"   📈 総CM記録数: {stat['total_cm_records']:,}件")
        print(f"   👥 CM経験タレント数: {stat['total_talents']:,}名")
        print(f"   🎬 現在CM出演記録数: {stat['current_cm_count']:,}件")
        print(f"   ⭐ 現在CM出演タレント数: {stat['current_cm_talents']:,}名")

        print("\n🏷️ 競合カテゴリコード使用状況（上位20）:")
        category_query = """
            SELECT
                rival_category_type_cd1,
                COUNT(*) as count,
                COUNT(CASE WHEN use_period_end::date >= CURRENT_DATE THEN 1 END) as current_count
            FROM m_talent_cm
            WHERE rival_category_type_cd1 IS NOT NULL
            GROUP BY rival_category_type_cd1
            ORDER BY count DESC
            LIMIT 20
        """
        categories = await conn.fetch(category_query)
        for cat in categories:
            current_rate = (cat['current_count'] / cat['count'] * 100) if cat['count'] > 0 else 0
            print(f"   コード{cat['rival_category_type_cd1']:2d}: 総{cat['count']:3d}件 (現在{cat['current_count']:2d}件, {current_rate:.1f}%)")

        print("\n🍫 菓子・氷菓・食品関連CM検索:")
        confectionery_query = """
            SELECT
                tc.account_id,
                ma.name_full_for_matching as name,
                tc.client_name,
                tc.product_name,
                tc.use_period_start,
                tc.use_period_end,
                tc.rival_category_type_cd1,
                CASE
                    WHEN tc.use_period_end::date >= CURRENT_DATE THEN '🔴出演中'
                    ELSE '⚫終了'
                END as status
            FROM m_talent_cm tc
            JOIN m_account ma ON tc.account_id = ma.account_id
            WHERE (
                tc.client_name ILIKE '%菓子%' OR
                tc.client_name ILIKE '%製菓%' OR
                tc.client_name ILIKE '%お菓子%' OR
                tc.client_name ILIKE '%グリコ%' OR
                tc.client_name ILIKE '%明治%' OR
                tc.client_name ILIKE '%森永%' OR
                tc.client_name ILIKE '%ロッテ%' OR
                tc.client_name ILIKE '%カルビー%' OR
                tc.product_name ILIKE '%菓子%' OR
                tc.product_name ILIKE '%チョコ%' OR
                tc.product_name ILIKE '%ガム%' OR
                tc.product_name ILIKE '%スイーツ%' OR
                tc.product_name ILIKE '%クッキー%' OR
                tc.product_name ILIKE '%ケーキ%' OR
                tc.product_name ILIKE '%飴%' OR
                tc.product_name ILIKE '%ビスケット%' OR
                tc.product_name ILIKE '%スナック%' OR
                tc.rival_category_type_cd1 IN (1, 2)  -- 食品系カテゴリコードと想定
            )
            ORDER BY tc.use_period_end DESC NULLS LAST
            LIMIT 20
        """
        confectionery_cms = await conn.fetch(confectionery_query)
        if confectionery_cms:
            for cm in confectionery_cms:
                print(f"   {cm['status']} {cm['name']} | {cm['client_name']} | {cm['product_name']}")
                print(f"     📅 期間: {cm['use_period_start']} ～ {cm['use_period_end']} | 🏷️ カテゴリ: {cm['rival_category_type_cd1']}")
        else:
            print("   ⚠️  菓子・氷菓関連のCMが見つかりませんでした")

        print("\n🎯 APIテスト結果上位タレントのCM状況:")
        talent_cm_check_query = """
            SELECT
                ma.account_id,
                ma.name_full_for_matching as name,
                COUNT(tc.account_id) as total_cm_count,
                COUNT(CASE WHEN tc.use_period_end::date >= CURRENT_DATE THEN 1 END) as current_cm_count,
                MAX(CASE WHEN tc.use_period_end::date >= CURRENT_DATE THEN tc.use_period_end END) as latest_current_end,
                ARRAY_AGG(DISTINCT tc.rival_category_type_cd1) FILTER (WHERE tc.rival_category_type_cd1 IS NOT NULL AND tc.use_period_end::date >= CURRENT_DATE) as current_categories
            FROM m_account ma
            LEFT JOIN m_talent_cm tc ON ma.account_id = tc.account_id
            WHERE ma.account_id IN (123, 234, 1111, 30, 1171, 651, 618, 1214, 1342, 920)
            GROUP BY ma.account_id, ma.name_full_for_matching
            ORDER BY ma.account_id
        """
        talent_cms = await conn.fetch(talent_cm_check_query)
        for talent in talent_cms:
            status_icon = "🔴" if talent['current_cm_count'] > 0 else "🟢"
            status = f"現在{talent['current_cm_count']}件出演中" if talent['current_cm_count'] > 0 else "現在未出演"
            print(f"   {status_icon} {talent['name']} (ID: {talent['account_id']}): 総CM{talent['total_cm_count']}件, {status}")
            if talent['latest_current_end']:
                print(f"     📅 最新CM終了予定: {talent['latest_current_end']}")
            if talent['current_categories']:
                categories = [str(c) for c in talent['current_categories'] if c is not None]
                print(f"     🏷️ 現在のカテゴリ: {', '.join(categories)}")

        print("\n📋 カテゴリコード詳細サンプル:")
        sample_categories_query = """
            SELECT
                rival_category_type_cd1,
                STRING_AGG(DISTINCT tc.client_name, ', ') as sample_clients,
                STRING_AGG(DISTINCT tc.product_name, ', ') as sample_products
            FROM m_talent_cm tc
            WHERE rival_category_type_cd1 IN (1, 2, 8, 9, 21, 28)  -- 主要カテゴリ
            GROUP BY rival_category_type_cd1
            ORDER BY rival_category_type_cd1
        """
        sample_cats = await conn.fetch(sample_categories_query)
        for cat in sample_cats:
            print(f"   🏷️ コード{cat['rival_category_type_cd1']}:")
            print(f"     クライアント例: {cat['sample_clients'][:100]}...")
            print(f"     商品例: {cat['sample_products'][:100]}...")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_cm_final())