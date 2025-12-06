#!/usr/bin/env python3
"""
m_accountシート完全インポート（確実な実装・VR照合スペースなし対応）
実行計画書EXECUTION_PLAN_20251202.md準拠

重要仕様:
- 必ずm_accountシート読み込み（4,819人）
- last_name + first_name → name（スペースなし「有吉弘行」）
- VR照合互換性確保
- 個別インサートで確実なデータ投入
"""

import pandas as pd
import unicodedata
import asyncio
import asyncpg
from datetime import datetime
import sys
import os

def normalize_name(name):
    """日本語名前の正規化（VR照合用）"""
    if pd.isna(name) or name is None:
        return None

    name_str = str(name).strip()
    if not name_str:
        return None

    # Unicode正規化（NFKC：濁点統合、全角統一）
    normalized = unicodedata.normalize('NFKC', name_str)
    normalized = normalized.strip()

    return normalized if normalized else None

def create_display_name_spaceless(last_name, first_name):
    """VR照合対応の名前生成（スペースなし）
    実行計画書仕様: last_name + first_name → name（スペースなし「有吉弘行」）
    """
    last = normalize_name(last_name)
    first = normalize_name(first_name)

    # スペースなし連結（VR照合仕様）
    if last and first:
        return f"{last}{first}"  # 例：「有吉弘行」（スペースなし）
    elif last:
        return last  # first_nameがない場合
    else:
        return None

async def main():
    print("=" * 80)
    print("m_accountシート確実インポート（VR照合対応・スペースなし実装）")
    print("実行計画書EXECUTION_PLAN_20251202.md準拠")
    print("=" * 80)

    # データベース接続設定
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL環境変数が設定されていません")
        sys.exit(1)

    excel_file = '/Users/lennon/projects/talent-casting-form/DB情報/Nowデータ_20251126.xlsx'
    sheet_name = 'm_account'  # 実行計画書で明確に指定

    print(f"Excel file: {excel_file}")
    print(f"Sheet: {sheet_name} (4,819人期待)")
    print()

    try:
        print(f"📥 m_accountシート読み込み中...")
        print(f"📖 Reading {excel_file}...")

        # Excelファイル読み込み（必ずm_accountシート）
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        print(f"   Total records: {len(df):,}")

        # データ構造確認
        if len(df) != 4819:
            print(f"⚠️  Warning: Expected 4,819 records, got {len(df):,}")

        # del_flag分布確認
        if 'del_flag' in df.columns:
            active_count = len(df[df['del_flag'] == 0])
            deleted_count = len(df[df['del_flag'] == 1])
            print(f"   Active records (del_flag=0): {active_count:,}")
            print(f"   Deleted records (del_flag=1): {deleted_count:,}")

        # first_name有無確認
        if 'first_name' in df.columns:
            with_first = len(df[df['first_name'].notna()])
            without_first = len(df[df['first_name'].isna()])
            print(f"   Records with first_name: {with_first:,}")
            print(f"   Records without first_name: {without_first:,}")
        print()

        # データベース接続
        print("🗄️ データベース接続中...")
        conn = await asyncpg.connect(database_url)

        try:
            # トランザクション開始
            async with conn.transaction():
                print("🧹 既存データクリア中...")

                # 外部キー制約順序で削除
                dependent_tables = [
                    'talent_keywords',
                    'talent_movies',
                    'talent_deal_results',
                    'talent_notes',
                    'talent_contacts',
                    'talent_pricing',
                    'talent_business_info',
                    'talent_media_experience',
                    'talent_cm_history',
                    'talent_images',
                    'talent_scores'
                ]

                for table in dependent_tables:
                    try:
                        result = await conn.execute(f"DELETE FROM {table}")
                        print(f"   ✅ Cleared: {table}")
                    except Exception as e:
                        print(f"   ⚠️  Warning: {table} - {str(e)}")

                # メインテーブル削除
                await conn.execute("DELETE FROM talents")
                print("   ✅ Cleared: talents")
                print()

                print("💾 m_accountデータ個別インサート中...")
                success_count = 0
                error_count = 0

                for index, row in df.iterrows():
                    try:
                        # 基本データ取得
                        account_id = int(row['account_id']) if pd.notna(row['account_id']) else None
                        last_name = str(row['last_name']).strip() if pd.notna(row['last_name']) else None
                        first_name = str(row['first_name']).strip() if pd.notna(row['first_name']) else None

                        if not account_id or not last_name:
                            error_count += 1
                            continue

                        # VR照合対応の名前生成（スペースなし）
                        display_name = create_display_name_spaceless(last_name, first_name)
                        if not display_name:
                            error_count += 1
                            continue

                        # 基本データのみ（データベース schema準拠）
                        kana = str(row['last_name_kana']).strip() if pd.notna(row['last_name_kana']) else None
                        gender = str(row['gender_type_cd']).strip() if pd.notna(row['gender_type_cd']) else None
                        category = str(row['act_genre']).strip() if pd.notna(row['act_genre']) else None
                        del_flag = int(row['del_flag']) if pd.notna(row['del_flag']) else 0

                        # birth_year計算（birthday から）
                        birth_year = None
                        if pd.notna(row['birthday']):
                            try:
                                if hasattr(row['birthday'], 'year'):
                                    birth_year = int(row['birthday'].year)
                                else:
                                    birth_date = pd.to_datetime(row['birthday'])
                                    birth_year = int(birth_date.year)
                            except:
                                birth_year = None

                        # 個別インサート（確実な実行）
                        await conn.execute("""
                            INSERT INTO talents
                            (account_id, name, kana, gender, birth_year, category, money_max_one_year, del_flag, created_at, updated_at)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
                        """, account_id, display_name, kana, gender, birth_year, category, None, del_flag)

                        success_count += 1

                        # 進捗表示
                        if success_count % 500 == 0:
                            print(f"   Processing: {success_count:,}/{len(df):,} ({success_count/len(df)*100:.1f}%)")

                    except Exception as e:
                        error_count += 1
                        if error_count <= 5:
                            print(f"   ❌ Error processing row {index+1}: {str(e)}")

                print()
                print("✅ Transaction committed! Verifying results...")

        except Exception as e:
            print(f"❌ Transaction Error: {str(e)}")
            await conn.close()
            sys.exit(1)

        # 結果確認
        print()
        print("📊 Import verification...")

        # 総数確認
        total_result = await conn.fetchval("SELECT COUNT(*) as count FROM talents")
        print(f"  Total records in database: {total_result:,}")

        # del_flag分布確認
        del_flag_stats = await conn.fetch("""
            SELECT del_flag, COUNT(*) as count
            FROM talents
            GROUP BY del_flag
            ORDER BY del_flag
        """)

        # account_id範囲確認
        id_range = await conn.fetchrow("""
            SELECT MIN(account_id) as min_id, MAX(account_id) as max_id
            FROM talents
        """)

        # 名前サンプル確認（VR照合形式・スペースなし）
        samples = await conn.fetch("""
            SELECT account_id, name
            FROM talents
            ORDER BY account_id
            LIMIT 5
        """)

        await conn.close()

        print()
        print("【実行結果】")
        print(f"  処理対象レコード: {len(df):,}件")
        print(f"  成功: {success_count:,}件")
        print(f"  エラー: {error_count}件")
        print(f"  成功率: {success_count/(success_count+error_count)*100:.1f}%")
        print()

        print("【データベース確認結果】")
        print(f"  総レコード数: {total_result:,}人")
        if id_range['min_id'] and id_range['max_id']:
            print(f"  account_id範囲: {id_range['min_id']} - {id_range['max_id']}")
        print()

        if del_flag_stats:
            print("📊 del_flag分布:")
            for stat in del_flag_stats:
                flag_name = '有効' if stat['del_flag'] == 0 else f'削除フラグ({stat["del_flag"]})'
                print(f"  {flag_name}: {stat['count']:,}人")
        print()

        print("🔍 名前サンプル（VR照合形式・スペースなし）:")
        for sample in samples:
            print(f"  ID{sample['account_id']}: \"{sample['name']}\"")
        print()

        # VR照合完了判定
        expected_total = 4819
        completion_rate = (total_result / expected_total) * 100
        print(f"✅ VR照合対応インポート進捗: {total_result:,}/{expected_total:,} ({completion_rate:.1f}%)")

        if completion_rate >= 99.5:
            print("🎉 VR照合対応！m_accountシート完全インポート成功！")
            print("📋 次のステップ: Phase 1.2 残り9シートのインポート（Phase 1.2）")
        else:
            print("⚠️ インポートが不完全です。確認が必要です。")

        print()
        print("=" * 80)
        print("m_accountシートインポート完了（スペースなし名前実装済み）")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())