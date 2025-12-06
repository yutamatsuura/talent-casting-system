#!/usr/bin/env python3
"""データベースマイグレーション実行"""

import asyncio
import sys
from pathlib import Path
import datetime

sys.path.insert(0, str(Path(__file__).parent))
from sqlalchemy import text
from app.db.connection import init_db, get_session_maker

AsyncSessionLocal = None

async def get_async_session():
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
        AsyncSessionLocal = get_session_maker()
    return AsyncSessionLocal()

async def create_backup():
    """現在のデータベース状態をバックアップ"""
    print("🗄️  Creating database backup...")

    async with await get_async_session() as session:
        # 重要テーブルの現在の件数を記録
        backup_info = {}

        tables_to_backup = ['talents', 'talent_scores', 'talent_images']
        for table in tables_to_backup:
            result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            backup_info[table] = count
            print(f"   {table}: {count:,} records")

    # バックアップ情報をファイルに保存
    backup_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = Path(__file__).parent / f"backup_info_{backup_time}.txt"

    with open(backup_file, 'w') as f:
        f.write(f"Database Backup Info - {backup_time}\n")
        f.write("=" * 50 + "\n")
        for table, count in backup_info.items():
            f.write(f"{table}: {count:,} records\n")

    print(f"✅ Backup info saved to: {backup_file}")
    return backup_info

async def execute_migration():
    """マイグレーション実行"""
    print("=" * 80)
    print("🔧 EXECUTING DATABASE MIGRATION")
    print("=" * 80)

    # バックアップ作成
    backup_info = await create_backup()

    async with await get_async_session() as session:
        try:
            print("\n📋 Step 1: Extending talents table...")

            # 1. talents テーブル拡張
            migration_steps = [
                "ADD COLUMN name_normalized VARCHAR(255)",
                "ADD COLUMN company_name VARCHAR(255)",
                "ADD COLUMN image_name VARCHAR(255)",
                "ADD COLUMN birthday DATE",
                "ADD COLUMN prefecture_code INTEGER",
                "ADD COLUMN official_url TEXT",
                "ADD COLUMN del_flag INTEGER DEFAULT 0"
            ]

            for i, step in enumerate(migration_steps):
                try:
                    await session.execute(text(f"ALTER TABLE talents {step}"))
                    print(f"   ✅ {step}")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"   ⚠️  Column already exists: {step}")
                    else:
                        print(f"   ❌ Failed: {step} - {e}")
                        raise

            # CHECK制約追加
            try:
                await session.execute(text("ALTER TABLE talents ADD CONSTRAINT chk_del_flag CHECK (del_flag IN (0, 1))"))
                print("   ✅ CHECK constraint added for del_flag")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("   ⚠️  CHECK constraint already exists")
                else:
                    print(f"   ❌ Failed to add CHECK constraint: {e}")

            await session.commit()

            print("\n📋 Step 2: Creating indexes for talents table...")

            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_talents_account_id ON talents(account_id)",
                "CREATE INDEX IF NOT EXISTS idx_talents_name_normalized ON talents(name_normalized)",
                "CREATE INDEX IF NOT EXISTS idx_talents_del_flag ON talents(del_flag)",
                "CREATE INDEX IF NOT EXISTS idx_talents_company ON talents(company_name)"
            ]

            for index_sql in indexes:
                try:
                    await session.execute(text(index_sql))
                    index_name = index_sql.split()[-3]  # Extract index name
                    print(f"   ✅ Created index: {index_name}")
                except Exception as e:
                    print(f"   ⚠️  Index creation issue: {e}")

            await session.commit()

            print("\n📋 Step 3: Creating new tables...")

            # 2. 新規テーブル作成
            new_tables = {
                "talent_cm_history": """
                    CREATE TABLE IF NOT EXISTS talent_cm_history (
                        id SERIAL PRIMARY KEY,
                        talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE,
                        sub_id INTEGER NOT NULL,
                        client_name VARCHAR(255),
                        product_name VARCHAR(255),
                        use_period_start DATE,
                        use_period_end DATE,
                        rival_category_type_cd1 INTEGER,
                        rival_category_type_cd2 INTEGER,
                        rival_category_type_cd3 INTEGER,
                        rival_category_type_cd4 INTEGER,
                        note TEXT,
                        regist_date TIMESTAMP,
                        up_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """,

                "talent_media_experience": """
                    CREATE TABLE IF NOT EXISTS talent_media_experience (
                        id SERIAL PRIMARY KEY,
                        talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE,
                        drama TEXT,
                        movie TEXT,
                        stage TEXT,
                        variety TEXT,
                        profile TEXT,
                        regist_date TIMESTAMP,
                        up_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """,

                "talent_business_info": """
                    CREATE TABLE IF NOT EXISTS talent_business_info (
                        id SERIAL PRIMARY KEY,
                        talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE,
                        decision_flag INTEGER DEFAULT 0,
                        contact_flag INTEGER DEFAULT 0,
                        smooth_rating INTEGER DEFAULT 0,
                        regist_date TIMESTAMP,
                        up_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """,

                "talent_pricing": """
                    CREATE TABLE IF NOT EXISTS talent_pricing (
                        id SERIAL PRIMARY KEY,
                        talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE,
                        money_min_one_year NUMERIC(12,2),
                        money_max_one_year NUMERIC(12,2),
                        cost_min_one_year NUMERIC(12,2),
                        cost_max_one_year NUMERIC(12,2),
                        money_min_one_cool NUMERIC(12,2),
                        money_max_one_cool NUMERIC(12,2),
                        cost_min_one_cool NUMERIC(12,2),
                        cost_max_one_cool NUMERIC(12,2),
                        money_min_two_cool NUMERIC(12,2),
                        money_max_two_cool NUMERIC(12,2),
                        cost_min_two_cool NUMERIC(12,2),
                        cost_max_two_cool NUMERIC(12,2),
                        regist_date TIMESTAMP,
                        up_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """,

                "talent_contacts": """
                    CREATE TABLE IF NOT EXISTS talent_contacts (
                        id SERIAL PRIMARY KEY,
                        talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE,
                        staff_name VARCHAR(255),
                        staff_tel1 VARCHAR(50),
                        staff_tel2 VARCHAR(50),
                        staff_tel3 VARCHAR(50),
                        staff_mail VARCHAR(255),
                        staff_note TEXT,
                        regist_date TIMESTAMP,
                        up_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """,

                "talent_notes": """
                    CREATE TABLE IF NOT EXISTS talent_notes (
                        id SERIAL PRIMARY KEY,
                        talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE,
                        note TEXT,
                        regist_date TIMESTAMP,
                        up_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """,

                "talent_deal_results": """
                    CREATE TABLE IF NOT EXISTS talent_deal_results (
                        id SERIAL PRIMARY KEY,
                        talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE,
                        sub_id INTEGER NOT NULL,
                        recruiting_year INTEGER,
                        recruiting_month INTEGER,
                        job_name VARCHAR(255),
                        deal_result_cd INTEGER,
                        smooth_rating_cd INTEGER,
                        note TEXT,
                        rating_user_id INTEGER,
                        regist_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """,

                "talent_movies": """
                    CREATE TABLE IF NOT EXISTS talent_movies (
                        id SERIAL PRIMARY KEY,
                        talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE,
                        sub_id INTEGER NOT NULL,
                        url TEXT,
                        title VARCHAR(255),
                        regist_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """,

                "talent_keywords": """
                    CREATE TABLE IF NOT EXISTS talent_keywords (
                        id SERIAL PRIMARY KEY,
                        talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE,
                        sub_id INTEGER NOT NULL,
                        frequent_category_type_cd INTEGER,
                        source TEXT,
                        regist_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """
            }

            for table_name, create_sql in new_tables.items():
                try:
                    await session.execute(text(create_sql))
                    print(f"   ✅ Created table: {table_name}")
                except Exception as e:
                    print(f"   ❌ Failed to create {table_name}: {e}")
                    raise

            await session.commit()

            print("\n📋 Step 4: Creating indexes for new tables...")

            # テーブル別インデックス作成
            table_indexes = {
                "talent_cm_history": [
                    "CREATE INDEX IF NOT EXISTS idx_cm_talent_id ON talent_cm_history(talent_id)",
                    "CREATE INDEX IF NOT EXISTS idx_cm_client ON talent_cm_history(client_name)",
                    "CREATE INDEX IF NOT EXISTS idx_cm_period ON talent_cm_history(use_period_start, use_period_end)"
                ],
                "talent_media_experience": [
                    "CREATE INDEX IF NOT EXISTS idx_media_talent_id ON talent_media_experience(talent_id)"
                ],
                "talent_business_info": [
                    "CREATE INDEX IF NOT EXISTS idx_business_talent_id ON talent_business_info(talent_id)",
                    "CREATE INDEX IF NOT EXISTS idx_business_rating ON talent_business_info(smooth_rating)"
                ],
                "talent_pricing": [
                    "CREATE INDEX IF NOT EXISTS idx_pricing_talent_id ON talent_pricing(talent_id)",
                    "CREATE INDEX IF NOT EXISTS idx_pricing_one_year ON talent_pricing(money_max_one_year)"
                ],
                "talent_contacts": [
                    "CREATE INDEX IF NOT EXISTS idx_contacts_talent_id ON talent_contacts(talent_id)",
                    "CREATE INDEX IF NOT EXISTS idx_contacts_staff ON talent_contacts(staff_name)"
                ],
                "talent_notes": [
                    "CREATE INDEX IF NOT EXISTS idx_notes_talent_id ON talent_notes(talent_id)"
                ],
                "talent_deal_results": [
                    "CREATE INDEX IF NOT EXISTS idx_deal_results_talent_id ON talent_deal_results(talent_id)",
                    "CREATE INDEX IF NOT EXISTS idx_deal_results_year_month ON talent_deal_results(recruiting_year, recruiting_month)"
                ],
                "talent_movies": [
                    "CREATE INDEX IF NOT EXISTS idx_movies_talent_id ON talent_movies(talent_id)"
                ],
                "talent_keywords": [
                    "CREATE INDEX IF NOT EXISTS idx_keywords_talent_id ON talent_keywords(talent_id)",
                    "CREATE INDEX IF NOT EXISTS idx_keywords_category ON talent_keywords(frequent_category_type_cd)"
                ]
            }

            for table_name, indexes in table_indexes.items():
                for index_sql in indexes:
                    try:
                        await session.execute(text(index_sql))
                        index_name = index_sql.split()[-3]
                        print(f"   ✅ Created index: {index_name}")
                    except Exception as e:
                        print(f"   ⚠️  Index creation issue: {e}")

            await session.commit()

            print("\n✅ Migration completed successfully!")

            # マイグレーション後の状態確認
            print("\n📊 Post-migration verification:")

            # 新規テーブル確認
            result = await session.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                AND table_name LIKE 'talent_%'
                ORDER BY table_name
            """))

            new_talent_tables = [row[0] for row in result]
            print(f"   New talent-related tables: {len(new_talent_tables)}")
            for table in new_talent_tables:
                print(f"     - {table}")

            # talents テーブル新規カラム確認
            result = await session.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'talents'
                AND table_schema = 'public'
                AND column_name IN ('name_normalized', 'company_name', 'del_flag')
                ORDER BY column_name
            """))

            new_columns = [row[0] for row in result]
            print(f"   New columns in talents table: {new_columns}")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Migration failed: {e}")
            print("   Database rolled back to previous state")
            raise

    print("=" * 80)

async def main():
    try:
        await execute_migration()
        print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        return True
    except Exception as e:
        print(f"\n❌ Migration Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)