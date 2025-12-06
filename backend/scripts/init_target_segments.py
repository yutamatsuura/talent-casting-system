"""ターゲット層マスタテーブル初期化スクリプト
作成日: 2025-11-28
目的: target_segments テーブル作成と8ターゲット層データ投入
"""
import asyncio
import asyncpg
import os
from pathlib import Path


async def init_target_segments():
    """target_segments テーブルとデータの初期化"""
    # 環境変数から DATABASE_URL を取得
    env_path = Path(__file__).parent.parent.parent / ".env.local"
    database_url = None

    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("DATABASE_URL="):
                database_url = line.strip().split("=", 1)[1]
                break

    if not database_url:
        raise ValueError("DATABASE_URL not found in .env.local")

    print(f"📊 Connecting to database: {database_url[:50]}...")

    # データベース接続
    conn = await asyncpg.connect(database_url)

    try:
        # テーブル削除（既存データをクリア）
        print("🗑️  Dropping existing target_segments table...")
        await conn.execute("DROP TABLE IF EXISTS target_segments CASCADE")

        # テーブル作成
        print("🔨 Creating target_segments table...")
        await conn.execute("""
            CREATE TABLE target_segments (
                id SERIAL PRIMARY KEY,
                code VARCHAR(10) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                gender VARCHAR(10) NOT NULL,
                age_range VARCHAR(50) NOT NULL,
                display_order INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # インデックス作成
        print("📇 Creating indexes...")
        await conn.execute(
            "CREATE INDEX idx_target_segments_code ON target_segments(code)"
        )
        await conn.execute(
            "CREATE INDEX idx_target_segments_display_order ON target_segments(display_order)"
        )

        # 初期データ投入（8ターゲット層）
        print("📥 Inserting initial data (8 target segments)...")
        target_segments_data = [
            (1, "M1", "男性12-19", "男性", "12-19", 1),
            (2, "F1", "女性12-19", "女性", "12-19", 2),
            (3, "M2", "男性20-34", "男性", "20-34", 3),
            (4, "F2", "女性20-34", "女性", "20-34", 4),
            (5, "M3", "男性35-49", "男性", "35-49", 5),
            (6, "F3", "女性35-49", "女性", "35-49", 6),
            (7, "M4", "男性50-69", "男性", "50-69", 7),
            (8, "F4", "女性50-69", "女性", "50-69", 8),
        ]

        await conn.executemany(
            """
            INSERT INTO target_segments (id, code, name, gender, age_range, display_order)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            target_segments_data,
        )

        # シーケンスをリセット
        await conn.execute("SELECT setval('target_segments_id_seq', 8, true)")

        # 確認クエリ
        print("✅ Verifying inserted data...")
        rows = await conn.fetch("SELECT * FROM target_segments ORDER BY display_order")

        print("\n📋 Target Segments:")
        print(f"{'ID':<5} {'Code':<10} {'Name':<20} {'Gender':<10} {'Age Range':<15}")
        print("-" * 70)
        for row in rows:
            print(
                f"{row['id']:<5} {row['code']:<10} {row['name']:<20} {row['gender']:<10} {row['age_range']:<15}"
            )

        print(f"\n✅ Successfully initialized {len(rows)} target segments!")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(init_target_segments())
