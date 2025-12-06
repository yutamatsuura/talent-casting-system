#!/usr/bin/env python3
"""完全タレントデータベーススキーマ設計"""

import asyncio
import sys
from pathlib import Path

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

def generate_complete_schema_design():
    """完全スキーマ設計生成"""
    print("=" * 80)
    print("🏗️  COMPLETE TALENT DATABASE SCHEMA DESIGN")
    print("=" * 80)

    schema_design = {
        # 既存テーブル拡張
        "talents_modifications": {
            "description": "既存talentsテーブルの拡張",
            "modifications": [
                "ADD COLUMN name_normalized VARCHAR(255)",  # スペース除去済み名前
                "ADD COLUMN company_name VARCHAR(255)",      # 事務所名
                "ADD COLUMN image_name VARCHAR(255)",        # 画像ファイル名
                "ADD COLUMN birthday DATE",                  # 生年月日
                "ADD COLUMN prefecture_code INTEGER",        # 都道府県コード
                "ADD COLUMN official_url TEXT",              # 公式URL
                "ADD COLUMN del_flag INTEGER DEFAULT 0",     # 削除フラグ
                "ADD CONSTRAINT chk_del_flag CHECK (del_flag IN (0, 1))"
            ],
            "indexes": [
                "CREATE INDEX idx_talents_account_id ON talents(account_id)",
                "CREATE INDEX idx_talents_name_normalized ON talents(name_normalized)",
                "CREATE INDEX idx_talents_del_flag ON talents(del_flag)",
                "CREATE INDEX idx_talents_company ON talents(company_name)"
            ]
        },

        # 新規テーブル群
        "new_tables": {
            "talent_cm_history": {
                "description": "CM出演履歴",
                "source_sheet": "m_talent_cm",
                "expected_records": "6,687件",
                "columns": [
                    "id SERIAL PRIMARY KEY",
                    "talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE",
                    "sub_id INTEGER NOT NULL",  # 同一タレント複数CM用
                    "client_name VARCHAR(255)",
                    "product_name VARCHAR(255)",
                    "use_period_start DATE",
                    "use_period_end DATE",
                    "rival_category_type_cd1 INTEGER",
                    "rival_category_type_cd2 INTEGER",
                    "rival_category_type_cd3 INTEGER",
                    "rival_category_type_cd4 INTEGER",
                    "note TEXT",
                    "regist_date TIMESTAMP",
                    "up_date TIMESTAMP",
                    "created_at TIMESTAMP DEFAULT NOW()",
                    "updated_at TIMESTAMP DEFAULT NOW()"
                ],
                "indexes": [
                    "CREATE INDEX idx_cm_talent_id ON talent_cm_history(talent_id)",
                    "CREATE INDEX idx_cm_client ON talent_cm_history(client_name)",
                    "CREATE INDEX idx_cm_period ON talent_cm_history(use_period_start, use_period_end)"
                ]
            },

            "talent_media_experience": {
                "description": "メディア出演経験",
                "source_sheet": "m_talent_media",
                "expected_records": "4,305件",
                "columns": [
                    "id SERIAL PRIMARY KEY",
                    "talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE",
                    "drama TEXT",
                    "movie TEXT",
                    "stage TEXT",
                    "variety TEXT",
                    "profile TEXT",
                    "regist_date TIMESTAMP",
                    "up_date TIMESTAMP",
                    "created_at TIMESTAMP DEFAULT NOW()",
                    "updated_at TIMESTAMP DEFAULT NOW()"
                ],
                "indexes": [
                    "CREATE INDEX idx_media_talent_id ON talent_media_experience(talent_id)"
                ]
            },

            "talent_business_info": {
                "description": "取引・営業情報",
                "source_sheet": "m_talent_deal",
                "expected_records": "3,698件",
                "columns": [
                    "id SERIAL PRIMARY KEY",
                    "talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE",
                    "decision_flag INTEGER DEFAULT 0",  # 決定フラグ
                    "contact_flag INTEGER DEFAULT 0",   # 連絡フラグ
                    "smooth_rating INTEGER DEFAULT 0",  # スムーズ評価
                    "regist_date TIMESTAMP",
                    "up_date TIMESTAMP",
                    "created_at TIMESTAMP DEFAULT NOW()",
                    "updated_at TIMESTAMP DEFAULT NOW()"
                ],
                "indexes": [
                    "CREATE INDEX idx_business_talent_id ON talent_business_info(talent_id)",
                    "CREATE INDEX idx_business_rating ON talent_business_info(smooth_rating)"
                ]
            },

            "talent_pricing": {
                "description": "料金情報",
                "source_sheet": "m_talent_act",
                "expected_records": "3,224件",
                "columns": [
                    "id SERIAL PRIMARY KEY",
                    "talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE",
                    "money_min_one_year NUMERIC(12,2)",
                    "money_max_one_year NUMERIC(12,2)",
                    "cost_min_one_year NUMERIC(12,2)",
                    "cost_max_one_year NUMERIC(12,2)",
                    "money_min_one_cool NUMERIC(12,2)",
                    "money_max_one_cool NUMERIC(12,2)",
                    "cost_min_one_cool NUMERIC(12,2)",
                    "cost_max_one_cool NUMERIC(12,2)",
                    "money_min_two_cool NUMERIC(12,2)",
                    "money_max_two_cool NUMERIC(12,2)",
                    "cost_min_two_cool NUMERIC(12,2)",
                    "cost_max_two_cool NUMERIC(12,2)",
                    "regist_date TIMESTAMP",
                    "up_date TIMESTAMP",
                    "created_at TIMESTAMP DEFAULT NOW()",
                    "updated_at TIMESTAMP DEFAULT NOW()"
                ],
                "indexes": [
                    "CREATE INDEX idx_pricing_talent_id ON talent_pricing(talent_id)",
                    "CREATE INDEX idx_pricing_one_year ON talent_pricing(money_max_one_year)"
                ]
            },

            "talent_contacts": {
                "description": "スタッフ連絡先",
                "source_sheet": "m_talent_staff",
                "expected_records": "4,232件",
                "columns": [
                    "id SERIAL PRIMARY KEY",
                    "talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE",
                    "staff_name VARCHAR(255)",
                    "staff_tel1 VARCHAR(50)",
                    "staff_tel2 VARCHAR(50)",
                    "staff_tel3 VARCHAR(50)",
                    "staff_mail VARCHAR(255)",
                    "staff_note TEXT",
                    "regist_date TIMESTAMP",
                    "up_date TIMESTAMP",
                    "created_at TIMESTAMP DEFAULT NOW()",
                    "updated_at TIMESTAMP DEFAULT NOW()"
                ],
                "indexes": [
                    "CREATE INDEX idx_contacts_talent_id ON talent_contacts(talent_id)",
                    "CREATE INDEX idx_contacts_staff ON talent_contacts(staff_name)"
                ]
            },

            "talent_notes": {
                "description": "備考・特記事項",
                "source_sheet": "m_talent_other",
                "expected_records": "4,487件",
                "columns": [
                    "id SERIAL PRIMARY KEY",
                    "talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE",
                    "note TEXT",
                    "regist_date TIMESTAMP",
                    "up_date TIMESTAMP",
                    "created_at TIMESTAMP DEFAULT NOW()",
                    "updated_at TIMESTAMP DEFAULT NOW()"
                ],
                "indexes": [
                    "CREATE INDEX idx_notes_talent_id ON talent_notes(talent_id)"
                ]
            },

            "talent_deal_results": {
                "description": "案件結果詳細",
                "source_sheet": "m_talent_deal_result",
                "expected_records": "27件",
                "columns": [
                    "id SERIAL PRIMARY KEY",
                    "talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE",
                    "sub_id INTEGER NOT NULL",
                    "recruiting_year INTEGER",
                    "recruiting_month INTEGER",
                    "job_name VARCHAR(255)",
                    "deal_result_cd INTEGER",
                    "smooth_rating_cd INTEGER",
                    "note TEXT",
                    "rating_user_id INTEGER",
                    "regist_date TIMESTAMP",
                    "created_at TIMESTAMP DEFAULT NOW()",
                    "updated_at TIMESTAMP DEFAULT NOW()"
                ],
                "indexes": [
                    "CREATE INDEX idx_deal_results_talent_id ON talent_deal_results(talent_id)",
                    "CREATE INDEX idx_deal_results_year_month ON talent_deal_results(recruiting_year, recruiting_month)"
                ]
            },

            "talent_movies": {
                "description": "動画情報",
                "source_sheet": "m_talent_movie",
                "expected_records": "1件",
                "columns": [
                    "id SERIAL PRIMARY KEY",
                    "talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE",
                    "sub_id INTEGER NOT NULL",
                    "url TEXT",
                    "title VARCHAR(255)",
                    "regist_date TIMESTAMP",
                    "created_at TIMESTAMP DEFAULT NOW()",
                    "updated_at TIMESTAMP DEFAULT NOW()"
                ],
                "indexes": [
                    "CREATE INDEX idx_movies_talent_id ON talent_movies(talent_id)"
                ]
            },

            "talent_keywords": {
                "description": "頻出キーワード",
                "source_sheet": "m_talent_frequent_keyword",
                "expected_records": "1,726件",
                "columns": [
                    "id SERIAL PRIMARY KEY",
                    "talent_id INTEGER NOT NULL REFERENCES talents(id) ON DELETE CASCADE",
                    "sub_id INTEGER NOT NULL",
                    "frequent_category_type_cd INTEGER",
                    "source TEXT",
                    "regist_date TIMESTAMP",
                    "created_at TIMESTAMP DEFAULT NOW()",
                    "updated_at TIMESTAMP DEFAULT NOW()"
                ],
                "indexes": [
                    "CREATE INDEX idx_keywords_talent_id ON talent_keywords(talent_id)",
                    "CREATE INDEX idx_keywords_category ON talent_keywords(frequent_category_type_cd)"
                ]
            }
        }
    }

    return schema_design

async def generate_migration_sql():
    """マイグレーションSQL生成"""
    schema_design = generate_complete_schema_design()

    print("\n📋 SCHEMA DESIGN SUMMARY:")
    print(f"   既存テーブル拡張: talents")
    print(f"   新規テーブル: {len(schema_design['new_tables'])}個")

    total_expected = 0
    for table_name, table_info in schema_design['new_tables'].items():
        records = table_info['expected_records'].replace('件', '').replace(',', '')
        if records.isdigit():
            total_expected += int(records)
        print(f"     - {table_name}: {table_info['expected_records']}")

    print(f"   新規データ総計: {total_expected:,}件")

    print("\n🔧 GENERATED MIGRATION SQL:")
    print("-- =============================================================================")
    print("-- COMPLETE TALENT DATABASE SCHEMA MIGRATION")
    print("-- =============================================================================")

    # talents テーブル拡張
    print("\n-- 1. Extend talents table")
    for modification in schema_design['talents_modifications']['modifications']:
        print(f"ALTER TABLE talents {modification};")

    print("\n-- 1.1. Add indexes for talents table")
    for index_sql in schema_design['talents_modifications']['indexes']:
        print(f"{index_sql};")

    # 新規テーブル作成
    print("\n-- 2. Create new tables")
    for table_name, table_info in schema_design['new_tables'].items():
        print(f"\n-- 2.{list(schema_design['new_tables'].keys()).index(table_name) + 1}. {table_info['description']} ({table_info['expected_records']})")
        print(f"CREATE TABLE {table_name} (")

        columns = table_info['columns']
        for i, column in enumerate(columns):
            comma = "," if i < len(columns) - 1 else ""
            print(f"    {column}{comma}")

        print(");")

        # インデックス作成
        if 'indexes' in table_info:
            print(f"\n-- Indexes for {table_name}")
            for index_sql in table_info['indexes']:
                print(f"{index_sql};")

    print("\n-- 3. Update talents.money_max_one_year from talent_pricing")
    print("""UPDATE talents
SET money_max_one_year = tp.money_max_one_year,
    updated_at = NOW()
FROM talent_pricing tp
WHERE talents.id = tp.talent_id
AND tp.money_max_one_year IS NOT NULL;""")

    print("\n-- =============================================================================")
    print("-- END MIGRATION SQL")
    print("-- =============================================================================")

    return schema_design

async def main():
    try:
        schema_design = await generate_migration_sql()

        print(f"\n✅ SCHEMA DESIGN COMPLETE")
        print(f"   Ready for implementation!")

        return schema_design
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    result = asyncio.run(main())