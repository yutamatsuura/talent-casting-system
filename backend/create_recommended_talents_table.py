#!/usr/bin/env python3
"""おすすめタレント設定テーブルの作成スクリプト

このスクリプトは recommended_talents テーブルを作成します。
業界別におすすめタレント3人を設定できる管理機能のためのテーブルです。
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.connection import get_asyncpg_connection

async def create_recommended_talents_table():
    """おすすめタレント設定テーブルの作成"""

    try:
        conn = await get_asyncpg_connection()

        print("🚀 おすすめタレント設定テーブルの作成を開始...")

        # テーブル作成SQL
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS recommended_talents (
                id SERIAL PRIMARY KEY,
                industry_name VARCHAR(100) NOT NULL,
                talent_id_1 INTEGER REFERENCES m_account(account_id),
                talent_id_2 INTEGER REFERENCES m_account(account_id),
                talent_id_3 INTEGER REFERENCES m_account(account_id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_industry_recommendation UNIQUE (industry_name)
            );
        """

        await conn.execute(create_table_sql)
        print("✅ recommended_talents テーブルが正常に作成されました")

        # インデックス作成
        index_sql = """
            CREATE INDEX IF NOT EXISTS idx_recommended_talents_industry
            ON recommended_talents(industry_name);
        """

        await conn.execute(index_sql)
        print("✅ インデックスが正常に作成されました")

        # 更新時刻を自動更新するトリガー関数とトリガーの作成
        trigger_function_sql = """
            CREATE OR REPLACE FUNCTION update_recommended_talents_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """

        await conn.execute(trigger_function_sql)
        print("✅ トリガー関数が正常に作成されました")

        trigger_sql = """
            DROP TRIGGER IF EXISTS update_recommended_talents_updated_at_trigger
            ON recommended_talents;

            CREATE TRIGGER update_recommended_talents_updated_at_trigger
                BEFORE UPDATE ON recommended_talents
                FOR EACH ROW
                EXECUTE FUNCTION update_recommended_talents_updated_at();
        """

        await conn.execute(trigger_sql)
        print("✅ トリガーが正常に作成されました")

        # サンプルデータの挿入（業界データが存在する場合）
        sample_data_sql = """
            INSERT INTO recommended_talents (industry_name, talent_id_1, talent_id_2, talent_id_3)
            SELECT
                i.industry_name,
                (SELECT account_id FROM m_account ORDER BY RANDOM() LIMIT 1),
                (SELECT account_id FROM m_account ORDER BY RANDOM() LIMIT 1),
                (SELECT account_id FROM m_account ORDER BY RANDOM() LIMIT 1)
            FROM industries i
            WHERE i.industry_name IN (
                '化粧品・ヘアケア・オーラルケア',
                '食品・飲料',
                'ファッション・アパレル'
            )
            ON CONFLICT (industry_name) DO NOTHING;
        """

        result = await conn.execute(sample_data_sql)
        print(f"✅ サンプルデータが挿入されました")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        raise
    finally:
        if 'conn' in locals():
            await conn.close()

async def verify_table_creation():
    """テーブル作成の確認"""

    try:
        conn = await get_asyncpg_connection()

        # テーブル存在確認
        check_table_sql = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'recommended_talents';
        """

        result = await conn.fetchrow(check_table_sql)

        if result:
            print("✅ recommended_talents テーブルが正常に作成されています")

            # レコード数確認
            count_sql = "SELECT COUNT(*) FROM recommended_talents;"
            count = await conn.fetchval(count_sql)
            print(f"📊 現在のレコード数: {count} 件")

            # 構造確認
            structure_sql = """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'recommended_talents'
                ORDER BY ordinal_position;
            """

            columns = await conn.fetch(structure_sql)

            print("📋 テーブル構造:")
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == "YES" else "NOT NULL"
                print(f"  - {col['column_name']}: {col['data_type']} ({nullable})")

        else:
            print("❌ recommended_talents テーブルが見つかりません")

    except Exception as e:
        print(f"❌ 確認エラー: {e}")
    finally:
        if 'conn' in locals():
            await conn.close()

async def main():
    """メイン実行関数"""
    print("🚀 おすすめタレント設定テーブル作成スクリプト開始")
    print("=" * 60)

    await create_recommended_talents_table()
    print("=" * 60)
    await verify_table_creation()

    print("=" * 60)
    print("🎉 おすすめタレント設定テーブル作成が完了しました！")

if __name__ == "__main__":
    asyncio.run(main())