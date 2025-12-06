#!/usr/bin/env python3
"""現在のデータベース構造とtalentsテーブル詳細分析"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sqlalchemy import select, text, inspect
from app.db.connection import init_db, get_session_maker

AsyncSessionLocal = None

async def get_async_session():
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
        AsyncSessionLocal = get_session_maker()
    return AsyncSessionLocal()

async def analyze_current_schema():
    """現在のデータベース構造詳細分析"""
    print("=" * 80)
    print("🔍 CURRENT DATABASE SCHEMA DETAILED ANALYSIS")
    print("=" * 80)

    async with await get_async_session() as session:
        # 1. talents テーブル構造詳細確認
        print("\n📋 TALENTS TABLE STRUCTURE:")
        result = await session.execute(text("""
            SELECT
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = 'talents'
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """))

        talent_columns = []
        for row in result:
            col_info = {
                'name': row[0],
                'type': row[1],
                'max_length': row[2],
                'nullable': row[3],
                'default': row[4]
            }
            talent_columns.append(col_info)

            length_str = f"({row[2]})" if row[2] else ""
            nullable_str = "NULL" if row[3] == "YES" else "NOT NULL"
            default_str = f" DEFAULT {row[4]}" if row[4] else ""
            print(f"   {row[0]:<25} {row[1]}{length_str:<15} {nullable_str:<10}{default_str}")

        # 2. talentsテーブルのサンプルデータ確認
        print(f"\n📊 TALENTS TABLE SAMPLE DATA:")
        result = await session.execute(text("SELECT * FROM talents LIMIT 5"))
        sample_data = result.fetchall()

        if sample_data:
            for i, row in enumerate(sample_data):
                print(f"   Row {i+1}:")
                for j, col_info in enumerate(talent_columns):
                    value = row[j] if j < len(row) else "N/A"
                    print(f"     {col_info['name']:<20}: {value}")
                print()

        # 3. 全テーブル一覧と構造確認
        print(f"\n📋 ALL TABLES STRUCTURE:")
        result = await session.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))

        all_tables = [row[0] for row in result]

        for table_name in all_tables:
            result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()

            # テーブル構造取得
            result = await session.execute(text(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                AND table_schema = 'public'
                ORDER BY ordinal_position
                LIMIT 10
            """))

            columns = [(row[0], row[1], row[2]) for row in result]

            print(f"\n🔍 Table: {table_name} ({count:,} records)")
            for col_name, col_type, nullable in columns[:5]:  # 最初の5列のみ
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                print(f"     {col_name:<20}: {col_type:<15} {nullable_str}")
            if len(columns) > 5:
                print(f"     ... and {len(columns) - 5} more columns")

        # 4. 制約・インデックス確認
        print(f"\n📋 CONSTRAINTS AND INDEXES:")

        # Primary Keys
        result = await session.execute(text("""
            SELECT tc.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_schema = 'public'
        """))

        print("   Primary Keys:")
        for table_name, column_name in result:
            print(f"     {table_name}.{column_name}")

        # Foreign Keys
        result = await session.execute(text("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
        """))

        print("   Foreign Keys:")
        for table_name, column_name, foreign_table, foreign_column in result:
            print(f"     {table_name}.{column_name} → {foreign_table}.{foreign_column}")

        # 5. データ型と値の分析
        print(f"\n📊 TALENTS DATA ANALYSIS:")

        # 名前関連データの分析
        result = await session.execute(text("""
            SELECT
                COUNT(*) as total_records,
                COUNT(name) as name_not_null,
                COUNT(kana) as kana_not_null,
                AVG(LENGTH(name)) as avg_name_length,
                MAX(LENGTH(name)) as max_name_length,
                MIN(LENGTH(name)) as min_name_length
            FROM talents
            WHERE name IS NOT NULL
        """))

        stats = result.fetchone()
        print(f"   Total records: {stats[0]:,}")
        print(f"   Name field populated: {stats[1]:,} ({stats[1]/stats[0]*100:.1f}%)")
        print(f"   Kana field populated: {stats[2]:,} ({stats[2]/stats[0]*100:.1f}%)")
        print(f"   Average name length: {stats[3]:.1f} characters")
        print(f"   Name length range: {stats[5]} - {stats[4]} characters")

        # 性別データ確認
        result = await session.execute(text("""
            SELECT gender, COUNT(*)
            FROM talents
            GROUP BY gender
            ORDER BY COUNT(*) DESC
        """))
        print(f"   Gender distribution:")
        for gender, count in result:
            print(f"     {gender}: {count:,}")

        # カテゴリデータ確認
        result = await session.execute(text("""
            SELECT category, COUNT(*)
            FROM talents
            GROUP BY category
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """))
        print(f"   Top 10 categories:")
        for category, count in result:
            print(f"     {category}: {count:,}")

    print("=" * 80)

async def main():
    try:
        await analyze_current_schema()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())