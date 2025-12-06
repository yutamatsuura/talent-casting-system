#!/usr/bin/env python3
"""
ターゲット層マスタ修正スクリプト
要件仕様書の正確な8セグメントに修正
"""

import asyncio
import asyncpg
import os
import sys

# データベース接続URL
DATABASE_URL = "postgresql://neondb_owner:npg_9fvZtIKj3gHe@ep-wild-art-a1dq56d3-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

async def fix_target_segments():
    """ターゲット層マスタの修正（要件仕様書準拠の8セグメント）"""
    print("🚀 ターゲット層マスタ修正開始...")

    try:
        # データベース接続
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ データベース接続成功")

        # 現在のデータを確認
        current_data = await conn.fetch('''
            SELECT id, code, name, gender, age_range, display_order
            FROM target_segments ORDER BY display_order
        ''')

        print(f"\n📋 現在のターゲット層データ（{len(current_data)}件）:")
        print("-" * 80)
        for row in current_data:
            print(f"{row['display_order']}. {row['code']}: {row['name']} ({row['gender']}, {row['age_range']}) (ID: {row['id']})")

        # 全データクリア
        await conn.execute('DELETE FROM target_segments')
        print("\n✅ 既存データクリア完了")

        # 要件仕様書準拠の正確な8セグメント
        required_segments = [
            ('F1', '女性20-34', '女性', '20-34歳', 1),
            ('F2', '女性35-49', '女性', '35-49歳', 2),
            ('F3', '女性50歳以上', '女性', '50歳以上', 3),
            ('M1', '男性20-34', '男性', '20-34歳', 4),
            ('M2', '男性35-49', '男性', '35-49歳', 5),
            ('M3', '男性50歳以上', '男性', '50歳以上', 6),
            ('Teen', '10代（高校生中心）', '全体', '13-19歳', 7),
            ('Senior', '60歳以上', '全体', '60歳以上', 8)
        ]

        # データ挿入
        for code, name, gender, age_range, order in required_segments:
            await conn.execute('''
                INSERT INTO target_segments (code, name, gender, age_range, display_order)
                VALUES ($1, $2, $3, $4, $5)
            ''', code, name, gender, age_range, order)

        print(f"✅ {len(required_segments)}件の正しいデータ挿入完了")

        # 検証
        result = await conn.fetch('''
            SELECT id, code, name, gender, age_range, display_order
            FROM target_segments ORDER BY display_order
        ''')

        print("\n📋 修正後のターゲット層マスタデータ一覧:")
        print("-" * 80)
        for row in result:
            print(f"{row['display_order']}. {row['code']}: {row['name']} ({row['gender']}, {row['age_range']}) (ID: {row['id']})")

        print(f"\n✅ ターゲット層マスタ修正完了（合計: {len(result)}件）")

        if len(result) == 8:
            print("✅ ターゲット層数が要件の8セグメントと一致しました")
        else:
            print(f"❌ ターゲット層数が要件と不一致です（期待値: 8、実際: {len(result)}）")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        try:
            await conn.close()
            print("✅ データベース接続終了")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(fix_target_segments())