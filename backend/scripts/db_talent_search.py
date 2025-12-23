#!/usr/bin/env python3
"""
データベース内のタレント名調査スクリプト
CSVで失敗した高スコアタレントの実際のDB名を調査
"""
import asyncio
import sys
from pathlib import Path

# 親ディレクトリをパスに追加
sys.path.append(str(Path(__file__).parent.parent))

from app.database import get_session_maker

async def search_talent_names():
    """失敗したタレント名の実際のDB名を調査"""
    session_maker = get_session_maker()

    # 失敗した高スコアタレント名（CSVから）
    failed_talents = [
        "B'z",
        "[ALEXANDROS]",
        "SAKURA（宮脇咲良/LE SSERAFIM）",
        "ØMI（登坂広臣（三代目 J SOUL BROTHERS））",
        "スピッツ",
        "EXILE",
        "Aimer",
        "秦基博",
        "フィッシャーズ",
        "星街すいせい"
    ]

    # ユーザーが提供したaccount_id情報
    known_account_ids = {
        1802: "B'z",
        2726: "[ALEXANDROS]",
        404: "SAKURA（宮脇咲良/LE SSERAFIM）",
        274: "ØMI（登坂広臣（三代目 J SOUL BROTHERS））"
    }

    async with session_maker() as session:
        print("=" * 80)
        print("🔍 データベース内タレント名調査")
        print("=" * 80)

        # 1. 指定されたaccount_idの実際の名前を調査
        print("\n📋 指定account_idの実際のDB名:")
        print("-" * 50)
        for account_id, expected_name in known_account_ids.items():
            result = await session.execute(
                'SELECT account_id, name_full_for_matching FROM m_account WHERE account_id = $1',
                (account_id,)
            )
            row = result.fetchone()
            if row:
                actual_name = row[1]
                print(f"ID {account_id}: \"{actual_name}\"")
                if actual_name != expected_name:
                    print(f"  ⚠️  期待値: \"{expected_name}\"")
                    print(f"  ⚠️  実際値: \"{actual_name}\"")
            else:
                print(f"ID {account_id}: ❌ NOT FOUND (削除済みまたは存在せず)")

        # 2. 部分マッチによる候補検索
        print(f"\n🔍 部分マッチ候補検索:")
        print("-" * 50)
        search_patterns = [
            ("B'z系", "SELECT account_id, name_full_for_matching FROM m_account WHERE (name_full_for_matching LIKE '%B%z%' OR name_full_for_matching LIKE '%ビーズ%') AND del_flag = 0"),
            ("ALEXANDROS系", "SELECT account_id, name_full_for_matching FROM m_account WHERE (name_full_for_matching LIKE '%ALEXANDROS%' OR name_full_for_matching LIKE '%アレキサンドロス%') AND del_flag = 0"),
            ("SAKURA系", "SELECT account_id, name_full_for_matching FROM m_account WHERE (name_full_for_matching LIKE '%SAKURA%' OR name_full_for_matching LIKE '%宮脇咲良%' OR name_full_for_matching LIKE '%サクラ%') AND del_flag = 0"),
            ("ØMI系", "SELECT account_id, name_full_for_matching FROM m_account WHERE (name_full_for_matching LIKE '%ØMI%' OR name_full_for_matching LIKE '%登坂広臣%') AND del_flag = 0"),
            ("スピッツ系", "SELECT account_id, name_full_for_matching FROM m_account WHERE (name_full_for_matching LIKE '%スピッツ%' OR name_full_for_matching LIKE '%SPITZ%') AND del_flag = 0"),
            ("EXILE系", "SELECT account_id, name_full_for_matching FROM m_account WHERE (name_full_for_matching LIKE '%EXILE%' OR name_full_for_matching LIKE '%エグザイル%') AND del_flag = 0"),
        ]

        for search_name, query in search_patterns:
            result = await session.execute(query)
            rows = result.fetchall()
            print(f"\n{search_name}:")
            if rows:
                for row in rows:
                    print(f"  ID {row[0]}: \"{row[1]}\"")
            else:
                print("  ❌ 該当なし")

        # 3. イチローの確認（既知の成功例）
        print(f"\n✅ 成功例の確認（イチロー）:")
        print("-" * 30)
        result = await session.execute(
            'SELECT account_id, name_full_for_matching FROM m_account WHERE account_id = $1 AND del_flag = 0',
            (647,)  # ユーザー提供の情報
        )
        row = result.fetchone()
        if row:
            print(f"ID 647: \"{row[1]}\"")
        else:
            print("ID 647: ❌ NOT FOUND")

        print("\n" + "=" * 80)
        print("🎯 調査完了")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(search_talent_names())