#!/usr/bin/env python3
"""デバッグ用: budget_rangesテーブルの内容を確認"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv('/Users/lennon/projects/talent-casting-form/.env.local')

async def check_budget_ranges():
    """budget_rangesテーブルの全データを表示"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL環境変数が見つかりません")
        return

    print(f"🔗 データベース接続中...")
    print(f"📡 接続先: {database_url[:50]}...")

    try:
        conn = await asyncpg.connect(database_url)
        print("✅ データベース接続成功")

        # テーブル存在確認
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = 'budget_ranges'
            )
        """)

        if not table_exists:
            print("❌ budget_rangesテーブルが存在しません")
            await conn.close()
            return

        print("✅ budget_rangesテーブル存在確認")

        # テーブル構造確認
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'budget_ranges'
            ORDER BY ordinal_position
        """)

        print("\n📋 テーブル構造:")
        for col in columns:
            print(f"  - {col['column_name']} ({col['data_type']}) {'NULL可' if col['is_nullable'] == 'YES' else 'NOT NULL'}")

        # 全データ確認
        rows = await conn.fetch("SELECT * FROM budget_ranges ORDER BY id")

        print(f"\n📊 予算区分マスタデータ (件数: {len(rows)}):")
        if rows:
            for row in rows:
                print(f"  ID: {row['id']} | name: '{row['name']}' | min: {row['min_amount']} | max: {row['max_amount']}")
        else:
            print("  ⚠️  データが0件です")

        # 特定の予算区分を検索
        target_budget = "1,000万円～3,000万円未満"
        found = await conn.fetchrow(
            "SELECT * FROM budget_ranges WHERE name = $1", target_budget
        )

        print(f"\n🔍 検索結果: '{target_budget}'")
        if found:
            print(f"  ✅ 見つかりました: ID={found['id']}, min={found['min_amount']}, max={found['max_amount']}")
        else:
            print(f"  ❌ 見つかりませんでした")

        await conn.close()
        print("\n✅ データベース接続終了")

    except Exception as e:
        print(f"❌ エラー発生: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_budget_ranges())