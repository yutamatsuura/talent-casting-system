#!/usr/bin/env python3
"""
account_id存在確認用簡易スクリプト
"""
import asyncio
from typing import Dict

# 既存のスクリプトからインポート
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.database import get_session_maker
from sqlalchemy import text

async def check_specific_account_ids():
    """指定されたaccount_idの存在を直接確認"""
    session_maker = get_session_maker()

    # 確認したいaccount_id
    check_ids = [1802, 2726, 404, 274, 647, 482]
    expected_names = {
        1802: "B'z",
        2726: "[ALEXANDROS]",
        404: "SAKURA（宮脇咲良/LE SSERAFIM）",
        274: "ØMI（登坂広臣（三代目 J SOUL BROTHERS））",
        647: "イチロー（成功例）",
        482: "ヒカキン（成功例）"
    }

    print("=" * 80)
    print("🔍 account_id直接確認")
    print("=" * 80)

    async with session_maker() as session:
        # 各account_idを直接確認
        for account_id in check_ids:
            result = await session.execute(
                text('SELECT account_id, name_full_for_matching, del_flag FROM m_account WHERE account_id = :account_id'),
                {'account_id': account_id}
            )
            row = result.fetchone()

            expected_name = expected_names.get(account_id, "不明")
            print(f"\nID {account_id} ({expected_name}):")

            if row:
                actual_name = row[1]
                del_flag = row[2]
                if del_flag == 0:
                    print(f"  ✅ 存在 (有効)")
                    print(f"  実際の名前: \"{actual_name}\"")
                else:
                    print(f"  ❌ 削除済み (del_flag = {del_flag})")
                    print(f"  削除された名前: \"{actual_name}\"")
            else:
                print(f"  ❌ 存在しません")

        # 部分マッチ検索も実行
        print(f"\n🔍 部分マッチ検索:")
        print("-" * 40)

        search_terms = ["B'z", "ALEXANDROS", "SAKURA", "ØMI", "登坂", "宮脇", "咲良"]

        for term in search_terms:
            result = await session.execute(
                text('SELECT account_id, name_full_for_matching FROM m_account WHERE name_full_for_matching LIKE :term AND del_flag = 0'),
                {'term': f'%{term}%'}
            )
            rows = result.fetchall()

            print(f"\n'{term}' を含む名前:")
            if rows:
                for row in rows[:3]:  # 上位3件
                    print(f"  ID {row[0]}: \"{row[1]}\"")
            else:
                print(f"  ❌ 該当なし")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(check_specific_account_ids())