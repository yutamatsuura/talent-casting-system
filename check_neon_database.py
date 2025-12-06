#!/usr/bin/env python3
"""
Neon PostgreSQL データベース状況確認スクリプト
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
import traceback

# .env.localファイルの読み込み
load_dotenv('.env.local')

class DatabaseChecker:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.connection = None
        self.cursor = None
        self.report = {
            'connection_status': None,
            'tables': {},
            'data_structure_issues': [],
            'recommended_actions': [],
            'samples': {}
        }

    def connect(self) -> bool:
        """データベースに接続"""
        if not self.database_url:
            self.report['connection_status'] = {
                'status': '❌',
                'error': 'DATABASE_URL環境変数が設定されていません'
            }
            return False

        try:
            start_time = time.time()
            self.connection = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor,
                connect_timeout=30
            )
            self.cursor = self.connection.cursor()
            connection_time = (time.time() - start_time) * 1000

            # データベース名を取得
            self.cursor.execute("SELECT current_database()")
            db_name = self.cursor.fetchone()['current_database']

            self.report['connection_status'] = {
                'status': '✅',
                'database_name': db_name,
                'connection_time_ms': f"{connection_time:.2f}",
                'error': 'なし'
            }
            return True

        except Exception as e:
            self.report['connection_status'] = {
                'status': '❌',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
            return False

    def check_tables(self):
        """テーブルの存在確認"""
        expected_tables = [
            'talents',
            'talent_scores',
            'talent_images',
            'industries',
            'target_segments',
            'budget_ranges',
            'image_items',
            'industry_images'
        ]

        try:
            # 存在するテーブル一覧を取得
            self.cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            existing_tables = [row['table_name'] for row in self.cursor.fetchall()]

            for table in expected_tables:
                if table in existing_tables:
                    self.report['tables'][table] = {'exists': True}
                else:
                    self.report['tables'][table] = {'exists': False}
                    self.report['data_structure_issues'].append(
                        f"⚠️ テーブル '{table}' が存在しません"
                    )

            # 予期しないテーブルもレポート
            unexpected = set(existing_tables) - set(expected_tables)
            if unexpected:
                self.report['unexpected_tables'] = list(unexpected)

        except Exception as e:
            self.report['table_check_error'] = str(e)

    def check_table_structure(self, table_name: str):
        """テーブル構造の詳細確認"""
        if not self.report['tables'].get(table_name, {}).get('exists'):
            return

        try:
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
                AND table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))

            columns = self.cursor.fetchall()
            self.report['tables'][table_name]['columns'] = len(columns)
            self.report['tables'][table_name]['column_details'] = [
                {
                    'name': col['column_name'],
                    'type': col['data_type'],
                    'nullable': col['is_nullable']
                } for col in columns
            ]

            # 特定のカラム確認（talentsテーブルの場合）
            if table_name == 'talents':
                column_names = [col['column_name'] for col in columns]
                if 'name' in column_names:
                    self.report['data_structure_issues'].append(
                        "⚠️ talents.name カラムが存在（name_full_for_matchingへの変更が必要かもしれません）"
                    )
                elif 'name_full_for_matching' not in column_names:
                    self.report['data_structure_issues'].append(
                        "⚠️ talents.name_full_for_matching カラムが存在しません"
                    )

            # レコード数取得
            self.cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = self.cursor.fetchone()['count']
            self.report['tables'][table_name]['record_count'] = count

            # 主キー情報取得
            self.cursor.execute("""
                SELECT a.attname
                FROM pg_index i
                JOIN pg_attribute a ON a.attrelid = i.indrelid
                AND a.attnum = ANY(i.indkey)
                WHERE i.indrelid = %s::regclass
                AND i.indisprimary
            """, (table_name,))

            primary_keys = [row['attname'] for row in self.cursor.fetchall()]
            if primary_keys:
                self.report['tables'][table_name]['primary_keys'] = primary_keys

            # 外部キー情報取得
            self.cursor.execute("""
                SELECT
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name = %s
            """, (table_name,))

            foreign_keys = self.cursor.fetchall()
            if foreign_keys:
                self.report['tables'][table_name]['foreign_keys'] = [
                    {
                        'column': fk['column_name'],
                        'references': f"{fk['foreign_table_name']}.{fk['foreign_column_name']}"
                    } for fk in foreign_keys
                ]

        except Exception as e:
            self.report['tables'][table_name]['error'] = str(e)

    def get_sample_data(self, table_name: str, limit: int = 5):
        """サンプルデータ取得"""
        if not self.report['tables'].get(table_name, {}).get('exists'):
            return

        try:
            self.cursor.execute(f"SELECT * FROM {table_name} LIMIT %s", (limit,))
            samples = self.cursor.fetchall()

            # JSON形式に変換可能な形に整形
            self.report['samples'][table_name] = [
                {k: str(v) if v is not None else None for k, v in sample.items()}
                for sample in samples
            ]

        except Exception as e:
            self.report['samples'][table_name] = {'error': str(e)}

    def check_data_integrity(self):
        """データ整合性確認"""
        try:
            # talents と talent_scores の整合性
            if (self.report['tables'].get('talents', {}).get('exists') and
                self.report['tables'].get('talent_scores', {}).get('exists')):

                self.cursor.execute("""
                    SELECT COUNT(*) as orphan_count
                    FROM talent_scores ts
                    LEFT JOIN talents t ON ts.talent_id = t.id
                    WHERE t.id IS NULL
                """)
                orphans = self.cursor.fetchone()['orphan_count']

                if orphans > 0:
                    self.report['data_structure_issues'].append(
                        f"⚠️ talent_scores に存在しないtalent_idを参照するレコードが {orphans} 件あります"
                    )

            # target_segments の範囲確認
            if self.report['tables'].get('target_segments', {}).get('exists'):
                self.cursor.execute("""
                    SELECT MIN(id) as min_id, MAX(id) as max_id, COUNT(*) as count
                    FROM target_segments
                """)
                seg_info = self.cursor.fetchone()
                self.report['target_segments_info'] = seg_info

        except Exception as e:
            self.report['integrity_check_error'] = str(e)

    def generate_recommendations(self):
        """推奨アクションの生成"""
        # テーブル不足の確認
        missing_tables = [
            table for table, info in self.report['tables'].items()
            if not info.get('exists')
        ]

        if missing_tables:
            self.report['recommended_actions'].append(
                f"1. 不足テーブルの作成: {', '.join(missing_tables)}"
            )

        # データ量の確認
        if self.report['tables'].get('talents', {}).get('record_count', 0) < 1000:
            self.report['recommended_actions'].append(
                "2. talentsテーブルのデータが少ない可能性があります（期待値: 約2,000件）"
            )

        # カラム名の問題
        if any("name" in issue for issue in self.report['data_structure_issues']):
            self.report['recommended_actions'].append(
                "3. talentsテーブルのカラム名を確認し、必要に応じて修正してください"
            )

        if not self.report['recommended_actions']:
            self.report['recommended_actions'].append(
                "データベース構造は概ね期待通りです。詳細な実装に進むことができます。"
            )

    def print_report(self):
        """レポートの出力"""
        print("\n" + "="*80)
        print("## データベース状況レポート")
        print("="*80)

        # 接続状況
        print(f"\n### 接続状況: {self.report['connection_status']['status']}")
        if self.report['connection_status']['status'] == '✅':
            print(f"- 接続先: {self.report['connection_status']['database_name']}")
            print(f"- 接続時間: {self.report['connection_status']['connection_time_ms']}ms")
        print(f"- エラー: {self.report['connection_status']['error']}")

        # テーブル状況
        existing_count = sum(1 for t in self.report['tables'].values() if t.get('exists'))
        print(f"\n### テーブル状況: {existing_count}/8")

        for table_name, info in sorted(self.report['tables'].items()):
            status = "✅" if info.get('exists') else "❌"
            if info.get('exists'):
                print(f"- {status} {table_name} (カラム数: {info.get('columns', '?')}, レコード数: {info.get('record_count', '?')})")
            else:
                print(f"- {status} {table_name} (存在しない)")

        # 予期しないテーブル
        if 'unexpected_tables' in self.report:
            print(f"\n### 予期しないテーブル:")
            for table in self.report['unexpected_tables']:
                print(f"- {table}")

        # データ構造の問題
        if self.report['data_structure_issues']:
            print("\n### データ構造の問題:")
            for issue in self.report['data_structure_issues']:
                print(f"- {issue}")
        else:
            print("\n### データ構造の問題:")
            print("- ✅ 重大な問題は検出されませんでした")

        # 推奨アクション
        print("\n### 推奨アクション:")
        for action in self.report['recommended_actions']:
            print(f"- {action}")

        # サンプルデータ（talentsテーブルの最初の2件のみ表示）
        if 'talents' in self.report['samples'] and isinstance(self.report['samples']['talents'], list):
            print("\n### Talentsテーブル サンプルデータ（2件）:")
            for i, sample in enumerate(self.report['samples']['talents'][:2], 1):
                print(f"\n#### レコード {i}:")
                for key, value in list(sample.items())[:5]:  # 最初の5カラムのみ
                    print(f"  - {key}: {value}")

        print("\n" + "="*80)

    def save_detailed_report(self):
        """詳細レポートをJSONファイルに保存"""
        filename = f"database_check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n詳細レポートを {filename} に保存しました")

    def run(self):
        """全チェックを実行"""
        print("Neon PostgreSQLデータベース チェック開始...")

        if not self.connect():
            self.print_report()
            return

        print("テーブル存在確認中...")
        self.check_tables()

        print("テーブル構造確認中...")
        for table_name in self.report['tables'].keys():
            self.check_table_structure(table_name)

        print("サンプルデータ取得中...")
        self.get_sample_data('talents', 5)
        self.get_sample_data('talent_scores', 10)
        self.get_sample_data('talent_images', 5)

        print("データ整合性確認中...")
        self.check_data_integrity()

        print("推奨アクション生成中...")
        self.generate_recommendations()

        self.print_report()
        self.save_detailed_report()

        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


if __name__ == "__main__":
    checker = DatabaseChecker()
    checker.run()