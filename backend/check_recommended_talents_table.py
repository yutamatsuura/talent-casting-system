#!/usr/bin/env python3
"""recommended_talentsテーブル構造確認"""
import asyncio
from app.db.connection import get_asyncpg_connection

async def check_recommended_talents_structure():
    """recommended_talentsテーブルの構造を確認"""
    conn = await get_asyncpg_connection()
    try:
        # テーブル構造確認
        columns_query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'recommended_talents'
        ORDER BY ordinal_position
        """
        columns_result = await conn.fetch(columns_query)
        print("📋 recommended_talents テーブル構造:")
        for row in columns_result:
            print(f"   {row['column_name']:<20} {row['data_type']:<15} nullable: {row['is_nullable']}")

        # サンプルデータ確認
        print("\n📝 サンプルデータ（上位5件）:")
        sample_data = await conn.fetch("SELECT * FROM recommended_talents LIMIT 5")
        if sample_data:
            # ヘッダー出力
            headers = list(sample_data[0].keys())
            print("   " + " | ".join(f"{h:<15}" for h in headers))
            print("   " + "-" * (len(headers) * 18))

            # データ出力
            for row in sample_data:
                values = [str(v)[:15] if v is not None else 'NULL' for v in row.values()]
                print("   " + " | ".join(f"{v:<15}" for v in values))

        # 業種との関連確認（実際のJOIN）
        print("\n🔗 実際のJOINテスト:")
        join_test = await conn.fetch("""
            SELECT rt.account_id, rt.ranking, i.industry_name
            FROM recommended_talents rt
            INNER JOIN industries i ON rt.industry_name = i.industry_name
            WHERE i.industry_name = '食品'
            ORDER BY rt.ranking LIMIT 3
        """)

        if join_test:
            print("   ✅ JOIN成功:")
            for row in join_test:
                print(f"      タレントID: {row['account_id']}, ランキング: {row['ranking']}, 業種: {row['industry_name']}")
        else:
            print("   ❌ JOINでデータが見つかりません")

    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_recommended_talents_structure())