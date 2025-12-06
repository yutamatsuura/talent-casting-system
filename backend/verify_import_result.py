#!/usr/bin/env python3
"""インポート結果の簡易確認スクリプト"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sqlalchemy import text
from app.db.connection import init_db, get_session_maker

AsyncSessionLocal = None


async def get_async_session():
    """非同期セッション取得"""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
        AsyncSessionLocal = get_session_maker()
    return AsyncSessionLocal()


async def verify():
    """インポート結果の検証"""
    print("=" * 80)
    print("タレントデータインポート結果 - 簡易確認")
    print("=" * 80)

    async with await get_async_session() as session:
        # 総レコード数
        result = await session.execute(text("SELECT COUNT(*) FROM talents"))
        total_count = result.scalar()
        print(f"\n総タレント数: {total_count:,}")

        # del_flag統計
        result = await session.execute(text("""
            SELECT del_flag, COUNT(*)
            FROM talents
            GROUP BY del_flag
            ORDER BY del_flag
        """))
        del_flag_stats = result.fetchall()
        print("\ndel_flag統計:")
        for flag, count in del_flag_stats:
            status = "Active" if flag == 0 else "Deleted"
            print(f"  {status} (del_flag={flag}): {count:,}")

        # first_name統計
        result = await session.execute(text("""
            SELECT
                COUNT(*) FILTER (WHERE first_name IS NOT NULL) as with_first,
                COUNT(*) FILTER (WHERE first_name IS NULL) as without_first
            FROM talents
        """))
        name_stats = result.fetchone()
        print("\n名前統計:")
        print(f"  first_nameあり: {name_stats[0]:,}")
        print(f"  first_nameなし: {name_stats[1]:,}")

        # サンプルレコード（最初の5件）
        result = await session.execute(text("""
            SELECT account_id, name, last_name, first_name, del_flag
            FROM talents
            ORDER BY account_id
            LIMIT 5
        """))
        samples = result.fetchall()
        print("\nサンプルレコード（最初の5件）:")
        print(f"  {'ID':<5} {'名前':<25} {'姓':<12} {'名':<12} {'削除'}")
        print("  " + "-" * 70)
        for record in samples:
            first_name_display = record[3] if record[3] else "(なし)"
            print(f"  {record[0]:<5} {record[1]:<25} {record[2]:<12} {first_name_display:<12} {record[4]}")

        # 最後の5件も確認
        result = await session.execute(text("""
            SELECT account_id, name, last_name, first_name, del_flag
            FROM talents
            ORDER BY account_id DESC
            LIMIT 5
        """))
        samples = result.fetchall()
        print("\nサンプルレコード（最後の5件）:")
        print(f"  {'ID':<5} {'名前':<25} {'姓':<12} {'名':<12} {'削除'}")
        print("  " + "-" * 70)
        for record in reversed(list(samples)):
            first_name_display = record[3] if record[3] else "(なし)"
            print(f"  {record[0]:<5} {record[1]:<25} {record[2]:<12} {first_name_display:<12} {record[4]}")

        # account_IDの連続性チェック
        result = await session.execute(text("""
            SELECT MIN(account_id), MAX(account_id)
            FROM talents
        """))
        min_id, max_id = result.fetchone()
        print(f"\naccount_ID範囲: {min_id} - {max_id}")

        expected_count = max_id - min_id + 1
        if total_count == expected_count:
            print(f"✅ account_IDは連続しています（欠番なし）")
        else:
            print(f"⚠️ account_IDに欠番があります（期待: {expected_count}, 実際: {total_count}）")

    print("\n" + "=" * 80)
    print("✅ 検証完了")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(verify())
