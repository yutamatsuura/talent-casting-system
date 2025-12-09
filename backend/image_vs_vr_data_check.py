#!/usr/bin/env python3
"""
イメージデータとVRデータの関係を正確に確認
"""
import asyncio
from app.db.connection import get_asyncpg_connection

async def check_image_vs_vr_data():
    print("🔍 イメージデータ vs VRデータの関係確認")
    print("=" * 60)

    conn = await get_asyncpg_connection()
    try:
        # 1. イメージデータがあるタレント数
        image_data_query = """
        SELECT COUNT(DISTINCT account_id) as image_talent_count
        FROM talent_images
        """
        image_result = await conn.fetchrow(image_data_query)
        image_count = image_result['image_talent_count']

        # 2. VRデータがあるタレント数
        vr_data_query = """
        SELECT COUNT(DISTINCT account_id) as vr_talent_count
        FROM talent_scores
        WHERE vr_popularity IS NOT NULL
        """
        vr_result = await conn.fetchrow(vr_data_query)
        vr_count = vr_result['vr_talent_count']

        # 3. 両方のデータがあるタレント数
        both_data_query = """
        SELECT COUNT(DISTINCT ti.account_id) as both_talent_count
        FROM talent_images ti
        INNER JOIN talent_scores ts ON ti.account_id = ts.account_id
        WHERE ts.vr_popularity IS NOT NULL
        """
        both_result = await conn.fetchrow(both_data_query)
        both_count = both_result['both_talent_count']

        # 4. イメージデータのみあるタレント数
        image_only_query = """
        SELECT COUNT(DISTINCT ti.account_id) as image_only_count
        FROM talent_images ti
        LEFT JOIN talent_scores ts ON ti.account_id = ts.account_id
        WHERE ts.vr_popularity IS NULL
        """
        image_only_result = await conn.fetchrow(image_only_query)
        image_only_count = image_only_result['image_only_count']

        # 5. VRデータのみあるタレント数
        vr_only_query = """
        SELECT COUNT(DISTINCT ts.account_id) as vr_only_count
        FROM talent_scores ts
        LEFT JOIN talent_images ti ON ts.account_id = ti.account_id
        WHERE ts.vr_popularity IS NOT NULL
          AND ti.account_id IS NULL
        """
        vr_only_result = await conn.fetchrow(vr_only_query)
        vr_only_count = vr_only_result['vr_only_count']

        print(f"\n📊 データ比較結果:")
        print(f"   イメージデータありタレント: {image_count:>4}名")
        print(f"   VRデータありタレント:       {vr_count:>4}名")
        print(f"   両方ともありタレント:       {both_count:>4}名")
        print(f"   イメージのみ:               {image_only_count:>4}名")
        print(f"   VRのみ:                    {vr_only_count:>4}名")

        # 6. 判定
        print(f"\n🎯 判定:")
        if image_count == vr_count:
            print("   ✅ イメージデータ数 = VRデータ数 → 同じタレント群の可能性が高い")
        else:
            print(f"   ⚠️  イメージデータ数({image_count}) ≠ VRデータ数({vr_count}) → 異なるタレント群")

        if both_count == image_count:
            print("   ✅ イメージデータがあるタレントは全員VRデータもある → 問題なし")
        else:
            print(f"   ⚠️  イメージデータがあってもVRデータがないタレント: {image_count - both_count}名")

        # 7. サンプル確認（イメージデータとVRデータの関係）
        print(f"\n\n📋 サンプル確認（イメージ・VR両方ありのタレント）:")

        sample_query = """
        SELECT
            ti.account_id,
            ma.name_full_for_matching,
            ti.image_funny,
            ti.image_clean,
            ts.vr_popularity,
            ts.tpr_power_score
        FROM talent_images ti
        INNER JOIN talent_scores ts ON ti.account_id = ts.account_id AND ts.target_segment_id = 1
        INNER JOIN m_account ma ON ti.account_id = ma.account_id
        WHERE ts.vr_popularity IS NOT NULL
        ORDER BY ts.vr_popularity DESC
        LIMIT 10
        """

        samples = await conn.fetch(sample_query)

        print("   ID   | 名前           | おもしろい | 清潔感 | VR人気度 | TPR")
        print("   " + "-" * 70)

        for sample in samples:
            name = (sample['name_full_for_matching'] or 'Unknown')[:12].ljust(12)
            funny = sample['image_funny'] or 0
            clean = sample['image_clean'] or 0
            vr = sample['vr_popularity'] or 0
            tpr = sample['tpr_power_score'] or 0
            print(f"   {sample['account_id']:>4} | {name} | {funny:>8} | {clean:>5} | {vr:>7} | {tpr:>3}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_image_vs_vr_data())