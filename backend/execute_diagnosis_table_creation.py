#!/usr/bin/env python3
"""
診断結果テーブル作成スクリプト

管理者向け診断履歴管理機能のためのテーブルを作成します。
"""

import asyncio
import os
import logging
from app.db.connection import get_asyncpg_connection

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_diagnosis_results_table():
    """diagnosis_resultsテーブルを作成"""

    create_table_sql = """
    -- 診断結果保存テーブル作成
    CREATE TABLE IF NOT EXISTS diagnosis_results (
        id SERIAL PRIMARY KEY,
        form_submission_id INTEGER NOT NULL REFERENCES form_submissions(id),
        ranking INTEGER NOT NULL,
        talent_account_id INTEGER NOT NULL,
        talent_name VARCHAR(255) NOT NULL,
        talent_category VARCHAR(255),
        matching_score DECIMAL(5,2) NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- インデックス作成（パフォーマンス向上）
    CREATE INDEX IF NOT EXISTS idx_diagnosis_results_submission_id ON diagnosis_results(form_submission_id);
    CREATE INDEX IF NOT EXISTS idx_diagnosis_results_ranking ON diagnosis_results(form_submission_id, ranking);

    -- コメント追加
    COMMENT ON TABLE diagnosis_results IS '診断結果タレント30名保存テーブル';
    COMMENT ON COLUMN diagnosis_results.form_submission_id IS 'フォーム送信IDとの紐付け';
    COMMENT ON COLUMN diagnosis_results.ranking IS '診断結果順位（1-30位）';
    COMMENT ON COLUMN diagnosis_results.talent_account_id IS 'タレントアカウントID';
    COMMENT ON COLUMN diagnosis_results.talent_name IS 'タレント名';
    COMMENT ON COLUMN diagnosis_results.talent_category IS 'タレントカテゴリ（女優、アイドル等）';
    COMMENT ON COLUMN diagnosis_results.matching_score IS 'マッチングスコア（86.0-99.7点）';
    """

    conn = None
    try:
        # データベース接続
        conn = await get_asyncpg_connection()
        logger.info("📊 データベース接続成功")

        # テーブル作成実行
        await conn.execute(create_table_sql)
        logger.info("✅ diagnosis_resultsテーブル作成完了")

        # テーブル確認
        table_check = await conn.fetchrow("""
            SELECT tablename
            FROM pg_tables
            WHERE tablename = 'diagnosis_results'
        """)

        if table_check:
            logger.info("🎯 テーブル作成確認成功: diagnosis_results")

            # カラム情報確認
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'diagnosis_results'
                ORDER BY ordinal_position
            """)

            logger.info("📋 テーブル構造:")
            for col in columns:
                logger.info(f"  - {col['column_name']}: {col['data_type']} (null: {col['is_nullable']})")

        else:
            logger.error("❌ テーブル作成確認失敗")

    except Exception as e:
        logger.error(f"❌ テーブル作成エラー: {str(e)}")
        raise

    finally:
        if conn:
            await conn.close()
            logger.info("📊 データベース接続終了")

async def main():
    """メイン実行関数"""
    print("🚀 診断結果テーブル作成開始")
    print("=" * 50)

    try:
        await create_diagnosis_results_table()
        print("\n" + "=" * 50)
        print("🎉 診断結果テーブル作成完了！")
        print("\n📋 次のステップ:")
        print("1. バックエンドサーバーを再起動")
        print("2. 診断を実行して結果保存をテスト")
        print("3. 管理画面で詳細モーダルの診断結果セクションを確認")

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")
        print("💡 解決方法:")
        print("- データベース接続情報を確認")
        print("- DATABASE_URL環境変数が正しく設定されているか確認")
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(main())