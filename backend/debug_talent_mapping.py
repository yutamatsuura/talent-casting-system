#!/usr/bin/env python3
"""talent_mapping作成の詳細デバッグ"""

import asyncio
from sqlalchemy import text
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from app.db.connection import init_db, get_session_maker

async def debug_talent_mapping():
    await init_db()
    session_maker = get_session_maker()
    async with session_maker() as session:
        # 元の方法（VRスクリプトと同じ）
        result = await session.execute(text("SELECT id, account_id, name_normalized FROM talents"))
        talent_mapping = {}
        skipped_talents = []
        total_talents = 0

        for row in result:
            total_talents += 1
            if row[2]:  # name_normalizedが存在する場合
                talent_mapping[row[2]] = row[0]
            else:
                skipped_talents.append({
                    'id': row[0],
                    'account_id': row[1],
                    'name_normalized': row[2]
                })

        print(f"🔍 talent_mapping作成詳細:")
        print(f"   データベース全件数: {total_talents}")
        print(f"   talent_mapping追加: {len(talent_mapping)}")
        print(f"   スキップ件数: {len(skipped_talents)}")

        if skipped_talents:
            print(f"\n❌ スキップされたtalent:")
            for talent in skipped_talents:
                print(f"   ID:{talent['id']} account_id:{talent['account_id']} name_normalized:「{talent['name_normalized']}」")

        # 重複check
        print(f"\n🔍 重複チェック:")
        name_counts = {}
        result2 = await session.execute(text("SELECT name_normalized FROM talents"))
        for row in result2:
            name = row[0]
            if name in name_counts:
                name_counts[name] += 1
            else:
                name_counts[name] = 1

        duplicates = {name: count for name, count in name_counts.items() if count > 1}
        if duplicates:
            print(f"   重複する名前: {len(duplicates)}件")
            for name, count in list(duplicates.items())[:5]:
                print(f"     「{name}」: {count}回")
        else:
            print("   重複なし")

        return len(talent_mapping)

if __name__ == "__main__":
    asyncio.run(debug_talent_mapping())