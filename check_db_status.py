#!/usr/bin/env python3
"""データベース状況確認スクリプト"""

import asyncio
import asyncpg
import os

async def check_db_status():
    """talentsテーブルの現在状況確認"""
    database_url = "postgresql://neondb_owner:npg_9fvZtIKj3gHe@ep-wild-art-a1dq56d3-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

    try:
        conn = await asyncpg.connect(database_url)

        # 1. 総数確認
        total_count = await conn.fetchval('SELECT COUNT(*) FROM talents')
        print(f'📊 現在のtalentsテーブル状況:')
        print(f'  総レコード数: {total_count:,}件')
        print()

        if total_count > 0:
            # 2. del_flag分布
            del_flag_stats = await conn.fetch('SELECT del_flag, COUNT(*) as count FROM talents GROUP BY del_flag ORDER BY del_flag')
            print('🔍 del_flag分布:')
            for stat in del_flag_stats:
                flag_name = '有効' if stat['del_flag'] == 0 else f'削除フラグ({stat["del_flag"]})'
                print(f'  {flag_name}: {stat["count"]:,}人')
            print()

            # 3. account_id範囲
            min_id = await conn.fetchval('SELECT MIN(account_id) FROM talents')
            max_id = await conn.fetchval('SELECT MAX(account_id) FROM talents')
            print(f'📈 account_id範囲: {min_id} - {max_id}')
            print()

            # 4. 名前サンプル（最初の5人）
            sample_data = await conn.fetch('SELECT account_id, name, last_name, first_name FROM talents ORDER BY account_id LIMIT 5')
            print('👤 名前サンプル（最初の5人）:')
            for row in sample_data:
                first_name = row['first_name'] if row['first_name'] else 'None'
                print(f'  ID{row["account_id"]}: "{row["name"]}" (姓: "{row["last_name"]}", 名: "{first_name}")')
            print()

            # 5. インポート完了確認
            expected_total = 4819
            completion_rate = (total_count / expected_total) * 100
            print(f'✅ インポート進捗: {total_count:,}/{expected_total:,} ({completion_rate:.1f}%)')

            if completion_rate >= 100:
                print('🎉 m_accountシート完全インポート完了！')
            else:
                print('⚠️ インポートが未完了です。再実行が必要です。')

        else:
            print('❌ talentsテーブルが空です。インポートを実行してください。')

        await conn.close()

    except Exception as e:
        print(f'❌ データベース接続エラー: {e}')

if __name__ == "__main__":
    asyncio.run(check_db_status())