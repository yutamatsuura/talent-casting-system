#!/usr/bin/env python3
"""
起用目的マスタテーブル作成スクリプト
7つの必須カテゴリを正確にセットアップ
"""

import asyncio
import asyncpg
import os
import sys

# データベース接続URL
DATABASE_URL = "postgresql://neondb_owner:npg_9fvZtIKj3gHe@ep-wild-art-a1dq56d3-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

async def create_purpose_objectives():
    """起用目的マスタテーブルの作成と初期データ投入"""
    print("🚀 起用目的マスタテーブル作成開始...")

    try:
        # データベース接続
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ データベース接続成功")

        # テーブル作成
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS purpose_objectives (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                display_order INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        print("✅ purpose_objectivesテーブル作成完了")

        # 既存データクリア
        await conn.execute('DELETE FROM purpose_objectives')
        print("✅ 既存データクリア完了")

        # 7つの必須カテゴリ（要件仕様書準拠）
        purpose_objectives = [
            ('ブランドイメージの向上', 1),
            ('商品・サービス認知度向上', 2),
            ('購買促進・売上拡大', 3),
            ('新商品・サービスの告知', 4),
            ('企業信頼度・安心感の向上', 5),
            ('ターゲット層の拡大', 6),
            ('競合他社との差別化', 7)
        ]

        # データ挿入
        for name, order in purpose_objectives:
            await conn.execute('''
                INSERT INTO purpose_objectives (name, display_order)
                VALUES ($1, $2)
            ''', name, order)

        print(f"✅ {len(purpose_objectives)}件のデータ挿入完了")

        # 検証
        result = await conn.fetch('''
            SELECT id, name, display_order
            FROM purpose_objectives
            ORDER BY display_order
        ''')

        print("\n📋 起用目的マスタデータ一覧:")
        print("-" * 50)
        for row in result:
            print(f"{row['display_order']}. {row['name']} (ID: {row['id']})")

        print(f"\n✅ 起用目的マスタテーブル作成完了（合計: {len(result)}件）")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)

    finally:
        try:
            await conn.close()
            print("✅ データベース接続終了")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(create_purpose_objectives())