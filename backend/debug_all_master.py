#!/usr/bin/env python3
"""デバッグ用: 全マスタテーブルの状況を確認"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv('/Users/lennon/projects/talent-casting-form/.env.local')

async def check_all_master_tables():
    """全マスタテーブルの件数とサンプルデータを確認"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL環境変数が見つかりません")
        return

    print(f"🔗 データベース接続中...")

    try:
        conn = await asyncpg.connect(database_url)
        print("✅ データベース接続成功")

        # 確認対象テーブル一覧
        tables = [
            "budget_ranges",
            "target_segments",
            "industries",
            "image_items",
            "talents",
            "talent_scores",
            "talent_images",
            "industry_images"
        ]

        print("\n📊 マスタテーブル状況調査:")
        print("=" * 60)

        for table in tables:
            # テーブル存在確認
            table_exists = await conn.fetchval(f"""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_name = '{table}'
                )
            """)

            if not table_exists:
                print(f"❌ {table}: テーブル存在しません")
                continue

            # 件数確認
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")

            # サンプルデータ取得
            if count > 0:
                sample = await conn.fetchrow(f"SELECT * FROM {table} LIMIT 1")
                sample_text = str(dict(sample))[:80] + "..."
                print(f"✅ {table}: {count}件 - サンプル: {sample_text}")
            else:
                print(f"⚠️  {table}: 0件（空テーブル）")

        print("\n" + "=" * 60)

        # 特別確認: CLAUDEファイルに記載されている予算区分があるかチェック
        print("\n🔍 CLAUDE.md記載の予算区分確認:")
        claude_budget = "1,000万円～3,000万円未満"
        found = await conn.fetchrow(
            "SELECT * FROM budget_ranges WHERE name = $1", claude_budget
        )

        if found:
            print(f"  ✅ '{claude_budget}' 存在します")
        else:
            print(f"  ❌ '{claude_budget}' 存在しません")

        # 予算区分の全リストを表示
        budget_list = await conn.fetch("SELECT name FROM budget_ranges ORDER BY display_order, id")
        if budget_list:
            print(f"\n📋 登録済み予算区分 ({len(budget_list)}件):")
            for i, budget in enumerate(budget_list, 1):
                print(f"  {i}. {budget['name']}")
        else:
            print("\n⚠️  予算区分が1件も登録されていません")

        await conn.close()
        print("\n✅ 調査完了")

    except Exception as e:
        print(f"❌ エラー発生: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_all_master_tables())