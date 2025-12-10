#!/usr/bin/env python3
"""
診断結果データの確認：VR人気度と従来スコア（base_power_score）の状況確認
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

        # 最新の診断結果を確認
        query = """
        SELECT
            dr.id,
            dr.form_submission_id,
            dr.ranking,
            dr.talent_name,
            ts.vr_popularity,
            ts.tpr_power_score,
            ts.base_power_score,
            ROUND((ts.vr_popularity + ts.tpr_power_score) / 2, 2) as calculated_base_score,
            (ts.base_power_score = ts.vr_popularity) as is_same_as_vr
        FROM diagnosis_results dr
        JOIN talent_scores ts ON dr.talent_account_id = ts.account_id
        WHERE dr.form_submission_id = (
            SELECT MAX(form_submission_id) FROM diagnosis_results
        )
        ORDER BY dr.ranking
        LIMIT 5;
        """

        results = await conn.fetch(query)

        if not results:
            print("📊 診断結果データが見つかりません")
            await conn.close()
            return

        print("📊 最新の診断結果データ確認:")
        print("順位 | タレント名 | VR人気度 | TPRスコア | DB従来スコア | 計算従来スコア | VR=従来?")
        print("-" * 80)

        for result in results:
            ranking = result['ranking']
            name = result['talent_name'][:10]
            vr_pop = float(result['vr_popularity']) if result['vr_popularity'] else 0
            tpr_score = float(result['tpr_power_score']) if result['tpr_power_score'] else 0
            db_base = float(result['base_power_score']) if result['base_power_score'] else 0
            calc_base = float(result['calculated_base_score']) if result['calculated_base_score'] else 0
            is_same = result['is_same_as_vr']

            print(f"{ranking:2} | {name:10} | {vr_pop:8.2f} | {tpr_score:8.2f} | {db_base:11.2f} | {calc_base:13.2f} | {'YES' if is_same else 'NO'}")

        # 統計情報
        stats_query = """
        SELECT
            COUNT(*) as total_count,
            COUNT(CASE WHEN ts.base_power_score = ts.vr_popularity THEN 1 END) as same_values_count,
            form_submission_id
        FROM diagnosis_results dr
        JOIN talent_scores ts ON dr.talent_account_id = ts.account_id
        WHERE dr.form_submission_id = (
            SELECT MAX(form_submission_id) FROM diagnosis_results
        )
        GROUP BY form_submission_id;
        """

        stats = await conn.fetchrow(stats_query)

        if stats:
            print(f"\n📈 統計情報 (診断結果ID: {stats['form_submission_id']}):")
            print(f"   総タレント数: {stats['total_count']}")
            print(f"   VR人気度=従来スコアの件数: {stats['same_values_count']}")
            print(f"   同値率: {stats['same_values_count']/stats['total_count']*100:.1f}%")

            if stats['same_values_count'] > 0:
                print(f"\n⚠️  {stats['same_values_count']}件でVR人気度と従来スコアが同じ値になっています！")
                print("   これがCSV出力で同じ値になる原因です。")
            else:
                print("\n✅ 全タレントでVR人気度と従来スコアが正しく異なる値になっています！")

        await conn.close()

    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    asyncio.run(main())