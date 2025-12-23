#!/usr/bin/env python3
"""
都道府県コードの正確なマッピングを調査
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
        # 主要都道府県コードの有名人を確認
        target_codes = [11, 12, 13, 14, 29, 23, 40, 30]  # 上位8コード

        for code in target_codes:
            print(f"\n🔍 pref_cd={code}の有名人（5件サンプル）:")
            query = """
            SELECT account_id, name_full_for_matching, pref_cd, company_name
            FROM m_account
            WHERE pref_cd = $1 AND del_flag = 0
            ORDER BY account_id
            LIMIT 5
            """
            results = await conn.fetch(query, code)

            if results:
                for row in results:
                    print(f"  {row['name_full_for_matching']} (ID: {row['account_id']})")
            else:
                print("  該当なし")

        # 神奈川県（標準コード14）を確認
        print(f"\n🔍 神奈川県出身として知られる有名人を検索:")
        kanagawa_names = ['中居正広', '木村拓哉', '稲垣吾郎', '香取慎吾', '草彅剛']

        for name in kanagawa_names:
            query = """
            SELECT account_id, name_full_for_matching, pref_cd, company_name
            FROM m_account
            WHERE name_full_for_matching LIKE $1 AND del_flag = 0
            """
            results = await conn.fetch(query, f'%{name}%')

            if results:
                for row in results:
                    print(f"  {row['name_full_for_matching']}: pref_cd={row['pref_cd']}")
            else:
                print(f"  {name}: 見つからず")

        # 大阪府出身として知られる有名人を確認
        print(f"\n🔍 大阪府出身として知られる有名人を検索:")
        osaka_names = ['明石家さんま', '浜田雅功', '松本人志', 'ダウンタウン', '今田耕司']

        for name in osaka_names:
            query = """
            SELECT account_id, name_full_for_matching, pref_cd, company_name
            FROM m_account
            WHERE name_full_for_matching LIKE $1 AND del_flag = 0
            """
            results = await conn.fetch(query, f'%{name}%')

            if results:
                for row in results:
                    print(f"  {row['name_full_for_matching']}: pref_cd={row['pref_cd']}")
            else:
                print(f"  {name}: 見つからず")

    except Exception as e:
        print(f"❌ エラー: {e}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())