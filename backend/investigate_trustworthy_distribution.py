#!/usr/bin/env python3
"""信頼できるスコアの分布調査"""
import asyncio
import asyncpg
from app.db.connection import get_asyncpg_connection

async def investigate_trustworthy_distribution():
    """男性20-34歳の信頼できるスコア分布を調査"""
    conn = await get_asyncpg_connection()
    try:
        print("=" * 80)
        print("🔍 信頼できるスコア分布調査（男性20-34歳）")
        print("=" * 80)

        target_segment_id = 11  # 男性20-34歳

        # 1. 信頼できるスコアの基本統計
        print("\n📊 1. 信頼できるスコア基本統計")
        stats_query = """
        SELECT
            COUNT(*) as total_count,
            MIN(image_trustworthy) as min_score,
            MAX(image_trustworthy) as max_score,
            AVG(image_trustworthy) as avg_score,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY image_trustworthy) as median_score,
            STDDEV(image_trustworthy) as stddev_score
        FROM talent_images
        WHERE target_segment_id = $1
          AND image_trustworthy IS NOT NULL
        """
        stats = await conn.fetchrow(stats_query, target_segment_id)
        print(f"総タレント数: {stats['total_count']}")
        print(f"最小値: {stats['min_score']}")
        print(f"最大値: {stats['max_score']}")
        print(f"平均値: {stats['avg_score']:.2f}")
        print(f"中央値: {stats['median_score']:.2f}")
        print(f"標準偏差: {stats['stddev_score']:.2f}")

        # 2. スコア分布（10点刻み）
        print("\n📈 2. スコア分布（10点刻み）")
        distribution_query = """
        SELECT
            CASE
                WHEN image_trustworthy = 0 THEN '0'
                WHEN image_trustworthy <= 10 THEN '1-10'
                WHEN image_trustworthy <= 20 THEN '11-20'
                WHEN image_trustworthy <= 30 THEN '21-30'
                WHEN image_trustworthy <= 40 THEN '31-40'
                WHEN image_trustworthy <= 50 THEN '41-50'
                WHEN image_trustworthy <= 60 THEN '51-60'
                WHEN image_trustworthy <= 70 THEN '61-70'
                WHEN image_trustworthy <= 80 THEN '71-80'
                WHEN image_trustworthy <= 90 THEN '81-90'
                ELSE '91-100'
            END as score_range,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
        FROM talent_images
        WHERE target_segment_id = $1
          AND image_trustworthy IS NOT NULL
        GROUP BY
            CASE
                WHEN image_trustworthy = 0 THEN '0'
                WHEN image_trustworthy <= 10 THEN '1-10'
                WHEN image_trustworthy <= 20 THEN '11-20'
                WHEN image_trustworthy <= 30 THEN '21-30'
                WHEN image_trustworthy <= 40 THEN '31-40'
                WHEN image_trustworthy <= 50 THEN '41-50'
                WHEN image_trustworthy <= 60 THEN '51-60'
                WHEN image_trustworthy <= 70 THEN '61-70'
                WHEN image_trustworthy <= 80 THEN '71-80'
                WHEN image_trustworthy <= 90 THEN '81-90'
                ELSE '91-100'
            END
        ORDER BY MIN(image_trustworthy)
        """
        distribution = await conn.fetch(distribution_query, target_segment_id)
        for row in distribution:
            print(f"  {row['score_range']:>6}: {row['count']:4d}人 ({row['percentage']:5.1f}%)")

        # 3. 千鳥周辺のスコア詳細
        print("\n🎯 3. 千鳥(6.30)周辺のスコア詳細")
        chidori_nearby_query = """
        SELECT
            ma.name_full_for_matching as name,
            ti.image_trustworthy,
            PERCENT_RANK() OVER (ORDER BY ti.image_trustworthy DESC) as percentile_rank,
            ROW_NUMBER() OVER (ORDER BY ti.image_trustworthy DESC) as rank_desc,
            ROW_NUMBER() OVER (ORDER BY ti.image_trustworthy ASC) as rank_asc
        FROM talent_images ti
        INNER JOIN m_account ma ON ti.account_id = ma.account_id
        WHERE ti.target_segment_id = $1
          AND ti.image_trustworthy BETWEEN 0 AND 15
        ORDER BY ti.image_trustworthy DESC
        """
        nearby_results = await conn.fetch(chidori_nearby_query, target_segment_id)

        print("スコア6.30周辺のタレント:")
        for i, result in enumerate(nearby_results[:20]):  # 上位20位まで
            if result['name'] == '千鳥':
                print(f"👉 {result['name']:<15} スコア:{result['image_trustworthy']:5.1f} 順位:{result['percentile_rank']:.3f} (降順:{result['rank_desc']:3d}位/昇順:{result['rank_asc']:3d}位) ⚠️")
            else:
                print(f"   {result['name']:<15} スコア:{result['image_trustworthy']:5.1f} 順位:{result['percentile_rank']:.3f} (降順:{result['rank_desc']:3d}位/昇順:{result['rank_asc']:3d}位)")

        # 4. 0点のタレント数確認
        print("\n❓ 4. 0点タレントの詳細確認")
        zero_score_query = """
        SELECT COUNT(*) as zero_count
        FROM talent_images
        WHERE target_segment_id = $1
          AND image_trustworthy = 0
        """
        zero_count = await conn.fetchrow(zero_score_query, target_segment_id)
        print(f"信頼できるスコアが0点のタレント数: {zero_count['zero_count']}人")

        # 5. 上位15%の境界値確認
        print("\n📊 5. 順位境界の詳細確認")
        percentile_query = """
        SELECT
            PERCENTILE_CONT(0.15) WITHIN GROUP (ORDER BY image_trustworthy DESC) as top_15_percent_boundary,
            PERCENTILE_CONT(0.30) WITHIN GROUP (ORDER BY image_trustworthy DESC) as top_30_percent_boundary,
            PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY image_trustworthy DESC) as top_50_percent_boundary
        FROM talent_images
        WHERE target_segment_id = $1
          AND image_trustworthy IS NOT NULL
        """
        percentiles = await conn.fetchrow(percentile_query, target_segment_id)
        print(f"上位15%境界値: {percentiles['top_15_percent_boundary']:.2f}")
        print(f"上位30%境界値: {percentiles['top_30_percent_boundary']:.2f}")
        print(f"上位50%境界値: {percentiles['top_50_percent_boundary']:.2f}")

        print("\n" + "=" * 80)
        if zero_count['zero_count'] > stats['total_count'] * 0.8:
            print("🚨 判明：大半のタレントが信頼できるスコア0点のため、")
            print("   わずか6.30点でも上位15%に入ってしまっています！")
        print("=" * 80)

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(investigate_trustworthy_distribution())