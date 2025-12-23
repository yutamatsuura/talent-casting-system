#!/usr/bin/env python3
"""
データベース内の全都道府県コードを調査して完全なマッピング表を作成
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
        # 全都道府県コードの分布を取得
        print("\n📊 データベース内の全都道府県コード分布:")
        distribution_query = """
        SELECT pref_cd, COUNT(*) as count
        FROM m_account
        WHERE del_flag = 0 AND pref_cd IS NOT NULL
        GROUP BY pref_cd
        ORDER BY pref_cd
        """
        results = await conn.fetch(distribution_query)

        all_codes = []
        for row in results:
            code = row['pref_cd']
            count = row['count']
            all_codes.append(code)
            print(f"  pref_cd={code}: {count}人")

        print(f"\n🔍 データベース内のコード総数: {len(all_codes)}個")
        print(f"🔍 コード一覧: {sorted(all_codes)}")

        # 各コードの代表的な有名人を取得（識別のため）
        print(f"\n🎭 各都道府県コードの代表的な有名人:")

        for code in sorted(all_codes):
            query = """
            SELECT name_full_for_matching
            FROM m_account
            WHERE pref_cd = $1 AND del_flag = 0
            ORDER BY account_id
            LIMIT 3
            """
            talent_results = await conn.fetch(query, code)

            if talent_results:
                talent_names = [row['name_full_for_matching'] for row in talent_results]
                print(f"  pref_cd={code:2d}: {', '.join(talent_names)}")

        # 47都道府県標準コードとの比較
        print(f"\n📋 標準JIS X 0401コードとの比較:")
        standard_prefectures = [
            "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
            "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
            "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
            "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
            "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
            "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
            "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
        ]

        print(f"標準47都道府県: {len(standard_prefectures)}個")
        print(f"DB内コード数: {len(all_codes)}個")

        # 欠けているコードがないか確認
        max_code = max(all_codes) if all_codes else 0
        missing_codes = []
        for i in range(1, max_code + 1):
            if i not in all_codes:
                missing_codes.append(i)

        if missing_codes:
            print(f"\n⚠️  欠番のコード: {missing_codes}")
        else:
            print(f"\n✅ コード1〜{max_code}まで連続です")

    except Exception as e:
        print(f"❌ エラー: {e}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())