#!/usr/bin/env python3
"""
CSV出力データの検証：VR人気度と従来スコアが本当に違う値なのか確認
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    try:
        # データベースに接続
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL環境変数が設定されていません")
            return

        conn = await asyncpg.connect(db_url)

        # 数名のタレントデータを確認
        query = """
        SELECT
            account_id,
            name,
            vr_popularity,
            tpr_power_score,
            base_power_score
        FROM talent_scores
        WHERE vr_popularity IS NOT NULL
        AND base_power_score IS NOT NULL
        ORDER BY vr_popularity DESC
        LIMIT 5;
        """

        results = await conn.fetch(query)

        print("📊 データベース直接確認:")
        print("ID | タレント名 | VR人気度 | TPRスコア | 従来スコア | VR=従来?")
        print("-" * 70)

        for result in results:
            account_id = result['account_id']
            name = result['name'] or "Unknown"
            vr_pop = float(result['vr_popularity']) if result['vr_popularity'] else 0
            tpr_score = float(result['tpr_power_score']) if result['tpr_power_score'] else 0
            base_power = float(result['base_power_score']) if result['base_power_score'] else 0

            is_same = abs(vr_pop - base_power) < 0.01  # 浮動小数点誤差を考慮

            print(f"{account_id:2} | {name[:10]:10} | {vr_pop:8.2f} | {tpr_score:8.2f} | {base_power:9.2f} | {'YES' if is_same else 'NO'}")

        # 統計情報
        stats_query = """
        SELECT
            COUNT(*) as total_count,
            COUNT(CASE WHEN ABS(vr_popularity - base_power_score) < 0.01 THEN 1 END) as same_values_count,
            AVG(vr_popularity) as avg_vr,
            AVG(base_power_score) as avg_base
        FROM talent_scores
        WHERE vr_popularity IS NOT NULL AND base_power_score IS NOT NULL;
        """

        stats = await conn.fetchrow(stats_query)

        print(f"\n📈 統計情報:")
        print(f"   総タレント数: {stats['total_count']}")
        print(f"   VR人気度=従来スコアの件数: {stats['same_values_count']}")
        print(f"   VR人気度平均: {stats['avg_vr']:.2f}")
        print(f"   従来スコア平均: {stats['avg_base']:.2f}")
        print(f"   同値率: {stats['same_values_count']/stats['total_count']*100:.1f}%")

        if stats['same_values_count'] == stats['total_count']:
            print("\n⚠️  全タレントでVR人気度と従来スコアが同じ値になっています！")
            print("   これがCSV出力で同じ値になる原因です。")

        await conn.close()

    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    asyncio.run(main())