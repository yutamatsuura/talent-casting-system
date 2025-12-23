#!/usr/bin/env python3
"""
いとうあさこのデータベースレコードを確認して都道府県コードを調査
"""

import asyncio
import sys
import os

# backendディレクトリをPATHに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

async def main():
    # データベース接続
    DATABASE_URL = settings.database_url
    print(f"🔍 データベース接続: {DATABASE_URL[:50]}...")

    # asyncpg用のURL変換
    from urllib.parse import urlparse
    parsed = urlparse(DATABASE_URL)

    # asyncpg接続パラメータ構築
    conn_params = {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "user": parsed.username,
        "password": parsed.password,
        "database": parsed.path.lstrip('/'),
    }

    # SSL設定
    if "neon.tech" in DATABASE_URL or "sslmode=require" in DATABASE_URL:
        conn_params['ssl'] = 'require'

    import asyncpg
    conn = await asyncpg.connect(**conn_params)

    try:
        # いとうあさこを検索（複数のパターンで）
        queries = [
            "SELECT account_id, name_full_for_matching, pref_cd, company_name FROM m_account WHERE name_full_for_matching LIKE '%いとう%あさこ%' AND del_flag = 0",
            "SELECT account_id, name_full_for_matching, pref_cd, company_name FROM m_account WHERE name_full_for_matching LIKE '%伊東%' AND del_flag = 0",
            "SELECT account_id, name_full_for_matching, pref_cd, company_name FROM m_account WHERE name_full_for_matching LIKE '%あさこ%' AND del_flag = 0"
        ]

        for i, query in enumerate(queries, 1):
            print(f"\n🔍 検索{i}: {query}")
            results = await conn.fetch(query)

            if results:
                print(f"✅ 検索結果 ({len(results)}件):")
                for row in results:
                    print(f"  ID: {row['account_id']}, 名前: {row['name_full_for_matching']}, pref_cd: {row['pref_cd']}, 事務所: {row['company_name']}")
            else:
                print("❌ 該当なし")

        # 都道府県コード12のタレントを確認（サンプル10件）
        print(f"\n🔍 都道府県コード12のタレント（サンプル10件）:")
        pref_12_query = "SELECT account_id, name_full_for_matching, pref_cd, company_name FROM m_account WHERE pref_cd = 12 AND del_flag = 0 LIMIT 10"
        results = await conn.fetch(pref_12_query)

        if results:
            print(f"✅ pref_cd=12のタレント ({len(results)}件):")
            for row in results:
                print(f"  ID: {row['account_id']}, 名前: {row['name_full_for_matching']}, pref_cd: {row['pref_cd']}, 事務所: {row['company_name']}")

        # 各都道府県コードの分布を確認
        print(f"\n📊 都道府県コード分布（上位20位）:")
        distribution_query = """
        SELECT pref_cd, COUNT(*) as count
        FROM m_account
        WHERE del_flag = 0 AND pref_cd IS NOT NULL
        GROUP BY pref_cd
        ORDER BY count DESC
        LIMIT 20
        """
        results = await conn.fetch(distribution_query)

        for row in results:
            print(f"  pref_cd={row['pref_cd']}: {row['count']}人")

    except Exception as e:
        print(f"❌ エラー: {e}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())