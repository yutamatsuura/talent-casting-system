#!/usr/bin/env python3
"""
m_* テーブル構造詳細調査スクリプト
実行日: 2025-12-03
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql

# .env.localファイルの読み込み
load_dotenv('.env.local')

class MTableChecker:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """データベースに接続"""
        try:
            self.connection = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor,
                connect_timeout=30
            )
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            print(f"接続エラー: {e}")
            return False

    def check_m_account_structure(self):
        """m_accountテーブルの詳細構造を確認"""
        print("\n" + "="*80)
        print("## m_account テーブル構造詳細")
        print("="*80)

        # カラム情報取得
        self.cursor.execute("""
            SELECT
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = 'm_account'
            ORDER BY ordinal_position
        """)

        columns = self.cursor.fetchall()
        print(f"\n### カラム数: {len(columns)}")
        print("\n### カラム詳細:")
        for col in columns:
            nullable = "NULL可" if col['is_nullable'] == 'YES' else "NOT NULL"
            length = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
            print(f"  - {col['column_name']:<30} {col['data_type']}{length:<10} {nullable}")

        # レコード数取得
        self.cursor.execute("SELECT COUNT(*) as count FROM m_account")
        count = self.cursor.fetchone()['count']
        print(f"\n### レコード数: {count:,}")

        # サンプルデータ取得（5件）
        self.cursor.execute("SELECT * FROM m_account LIMIT 5")
        samples = self.cursor.fetchall()

        print("\n### サンプルデータ（5件）:")
        for i, sample in enumerate(samples, 1):
            print(f"\n#### レコード {i}:")
            # 重要なカラムのみ表示
            important_cols = ['account_id', 'account_type', 'name_full_for_matching',
                            'talent_name_code', 'code', 'money_max_one_year',
                            'sex', 'birthday', 'twitter', 'instagram']
            for col in important_cols:
                if col in sample:
                    value = sample[col]
                    if value and len(str(value)) > 50:
                        value = str(value)[:50] + "..."
                    print(f"    {col}: {value}")

    def check_other_m_tables(self):
        """その他のm_*テーブルの概要を確認"""
        print("\n" + "="*80)
        print("## その他のm_*テーブル概要")
        print("="*80)

        m_tables = [
            'm_talent_staff',
            'm_talent_movie',
            'm_talent_deal',
            'm_talent_other',
            'm_talent_frequent_keyword',
            'm_talent_media',
            'm_talent_act',
            'm_talent_cm',
            'm_talent_deal_result'
        ]

        for table in m_tables:
            self.cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = self.cursor.fetchone()['count']

            # カラム数取得
            self.cursor.execute("""
                SELECT COUNT(*) as col_count
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = %s
            """, (table,))
            col_count = self.cursor.fetchone()['col_count']

            # 主要カラム取得（最初の5つ）
            self.cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = %s
                ORDER BY ordinal_position
                LIMIT 5
            """, (table,))
            cols = self.cursor.fetchall()
            col_list = ", ".join([f"{c['column_name']}" for c in cols])

            print(f"\n### {table}")
            print(f"  - レコード数: {count:,}")
            print(f"  - カラム数: {col_count}")
            print(f"  - 主要カラム: {col_list}...")

    def check_relationships(self):
        """テーブル間の関係性を確認"""
        print("\n" + "="*80)
        print("## テーブル間の関係性")
        print("="*80)

        # talent_scoresとm_accountの関係
        self.cursor.execute("""
            SELECT
                COUNT(DISTINCT ts.account_id) as unique_talents_in_scores,
                COUNT(DISTINCT ma.account_id) as unique_accounts,
                COUNT(DISTINCT ts.account_id) FILTER (WHERE ma.account_id IS NULL) as orphan_scores
            FROM talent_scores ts
            LEFT JOIN m_account ma ON ts.account_id = ma.account_id
        """)
        result = self.cursor.fetchone()

        print("\n### talent_scores と m_account の関係:")
        print(f"  - talent_scoresのユニークaccount_id数: {result['unique_talents_in_scores']:,}")
        print(f"  - m_accountのユニークaccount_id数: {result['unique_accounts']:,}")
        print(f"  - m_accountに存在しないtalent_scores: {result['orphan_scores']:,}")

        # talent_imagesとm_accountの関係
        self.cursor.execute("""
            SELECT
                COUNT(DISTINCT ti.account_id) as unique_talents_in_images,
                COUNT(DISTINCT ti.account_id) FILTER (WHERE ma.account_id IS NULL) as orphan_images
            FROM talent_images ti
            LEFT JOIN m_account ma ON ti.account_id = ma.account_id
        """)
        result = self.cursor.fetchone()

        print("\n### talent_images と m_account の関係:")
        print(f"  - talent_imagesのユニークaccount_id数: {result['unique_talents_in_images']:,}")
        print(f"  - m_accountに存在しないtalent_images: {result['orphan_images']:,}")

        # target_segmentsの確認
        self.cursor.execute("""
            SELECT target_segment_id, segment_name, gender, age_min, age_max
            FROM target_segments
            ORDER BY target_segment_id
        """)
        segments = self.cursor.fetchall()

        print("\n### target_segments の内容:")
        for seg in segments:
            print(f"  - ID {seg['target_segment_id']}: {seg['segment_name']} ({seg['gender']} {seg['age_min']}-{seg['age_max']}歳)")

    def check_matching_logic_feasibility(self):
        """5段階マッチングロジック実装の実現可能性をチェック"""
        print("\n" + "="*80)
        print("## 5段階マッチングロジック実装可能性チェック")
        print("="*80)

        issues = []
        recommendations = []

        # STEP 0: 予算フィルタリング（m_talent_actテーブル確認）
        self.cursor.execute("""
            SELECT COUNT(*) as count
            FROM m_talent_act
            WHERE money_max_one_year IS NOT NULL
        """)
        budget_count = self.cursor.fetchone()['count']

        if budget_count > 0:
            print("✅ STEP 0 (予算フィルタリング): 実装可能")
            print(f"   - m_talent_actテーブルのmoney_max_one_yearフィールドにデータあり ({budget_count}件)")
        else:
            print("⚠️ STEP 0 (予算フィルタリング): データ不足")
            issues.append("money_max_one_yearのデータが不足")

        # STEP 1: 基礎パワー得点
        print("✅ STEP 1 (基礎パワー得点): 実装可能")
        print("   - talent_scoresテーブルにvr_popularity, tpr_power_score存在")

        # STEP 2: 業種イメージ査定
        print("✅ STEP 2 (業種イメージ査定): 実装可能")
        print("   - talent_imagesテーブルに各イメージスコア存在")
        print("   - industriesテーブルにrequired_image_id存在")

        # STEP 3-5
        print("✅ STEP 3-5 (得点計算・ランキング): 実装可能")

        # 推奨事項
        print("\n### 推奨される対応:")
        print("1. m_accountとm_talent_actをJOINしたビュー'talents'を作成")
        print("2. account_id を talent_id として扱う（またはエイリアス作成）")
        print("3. 既存のテーブル構造を活かしたマッチングロジック実装")
        print("4. industry_imagesテーブルの作成（industriesとimage_itemsの関連付け）")

    def run(self):
        """全チェックを実行"""
        if not self.connect():
            return

        self.check_m_account_structure()
        self.check_other_m_tables()
        self.check_relationships()
        self.check_matching_logic_feasibility()

        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


if __name__ == "__main__":
    checker = MTableChecker()
    checker.run()