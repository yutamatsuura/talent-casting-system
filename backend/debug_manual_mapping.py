#!/usr/bin/env python3
"""
手動マッピング辞書のデバッグ
"""
import asyncio
from app.database import get_session_maker

async def debug_manual_mapping():
    session_maker = get_session_maker()
    async with session_maker() as session:
        # 対象のaccount_idを調査
        target_account_ids = [1802, 2726, 404, 274]

        print("=== 実際のDB名前調査 ===")
        for account_id in target_account_ids:
            result = await session.execute(
                'SELECT account_id, name_full_for_matching FROM m_account WHERE account_id = $1 AND del_flag = 0',
                (account_id,)
            )
            row = result.fetchone()
            if row:
                print(f'account_id {account_id}: "{row[1]}"')
            else:
                print(f'account_id {account_id}: NOT FOUND OR DELETED')

        print("\n=== 手動マッピング辞書テスト ===")
        from scripts.talent_name_mapping_dictionary import get_manual_mapping, get_alternative_names

        test_names = ["B'z", "[ALEXANDROS]", "SAKURA（宮脇咲良/LE SSERAFIM）", "ØMI（登坂広臣（三代目 J SOUL BROTHERS））"]

        for name in test_names:
            manual = get_manual_mapping(name)
            alternatives = get_alternative_names(name)
            print(f'CSV名: "{name}"')
            print(f'  手動マッピング: {manual}')
            print(f'  代替候補: {alternatives}')
            print()

if __name__ == "__main__":
    asyncio.run(debug_manual_mapping())