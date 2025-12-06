#!/usr/bin/env python3
"""カテゴリマスターテーブルの検索"""
import asyncio
import asyncpg
from app.core.config import settings

async def search_category_master():
    """カテゴリマスターテーブルを検索"""
    print("=== カテゴリマスターテーブル検索 ===")

    conn = await asyncpg.connect(settings.database_url)
    try:
        # 全テーブル一覧を取得
        print("\n1. 全テーブル一覧:")
        tables_query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        tables = await conn.fetch(tables_query)
        for table in tables:
            print(f"  - {table['table_name']}")

        print("\n2. カテゴリ・競合関連のテーブル検索:")
        category_tables_query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND (table_name ILIKE '%category%'
                   OR table_name ILIKE '%rival%'
                   OR table_name ILIKE '%master%'
                   OR table_name ILIKE '%m_%'
                   OR table_name ILIKE '%type%')
            ORDER BY table_name
        """
        category_tables = await conn.fetch(category_tables_query)
        if category_tables:
            for table in category_tables:
                print(f"  🎯 {table['table_name']}")

                # テーブル構造を確認
                try:
                    columns_query = f"""
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_name = '{table['table_name']}'
                        ORDER BY ordinal_position
                        LIMIT 10
                    """
                    columns = await conn.fetch(columns_query)
                    for col in columns:
                        print(f"     - {col['column_name']}: {col['data_type']}")
                    print()
                except Exception as e:
                    print(f"     ❌ エラー: {e}\n")
        else:
            print("  ❌ カテゴリ関連テーブルが見つかりません")

        print("\n3. rival_category_type_cdに関連するテーブルの検索:")
        rival_related_query = """
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE column_name ILIKE '%rival%' OR column_name ILIKE '%category%'
            ORDER BY table_name, column_name
        """
        rival_columns = await conn.fetch(rival_related_query)
        if rival_columns:
            for col in rival_columns:
                print(f"  📋 {col['table_name']}.{col['column_name']}: {col['data_type']}")
        else:
            print("  ❌ rival/category関連カラムが見つかりません")

        print("\n4. m_で始まるマスターテーブルの詳細確認:")
        master_tables = [t['table_name'] for t in tables if t['table_name'].startswith('m_')]
        for table_name in master_tables:
            try:
                # サンプルデータを取得
                sample_query = f"SELECT * FROM {table_name} LIMIT 3"
                samples = await conn.fetch(sample_query)

                if samples:
                    print(f"\n  📊 {table_name} (サンプル{len(samples)}件):")
                    for i, sample in enumerate(samples, 1):
                        sample_dict = dict(sample)
                        # 長いデータは省略
                        for key, value in sample_dict.items():
                            if isinstance(value, str) and len(str(value)) > 50:
                                sample_dict[key] = f"{str(value)[:50]}..."
                        print(f"    {i}. {sample_dict}")
                else:
                    print(f"\n  📊 {table_name}: データなし")

            except Exception as e:
                print(f"\n  ❌ {table_name}: エラー - {e}")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(search_category_master())