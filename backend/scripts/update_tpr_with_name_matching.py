#!/usr/bin/env python3
"""
TPRパワースコア更新スクリプト（名前マッチング対応版）

機能:
- CSVファイルからG列のパワースコアを取り込み
- タレント名でのマッチング処理
- マッチング失敗時の詳細レポート生成
- base_power_scoreの自動更新
- ドライラン機能

使用方法:
    python update_tpr_with_name_matching.py --dry-run
    python update_tpr_with_name_matching.py --execute
"""

import argparse
import asyncio
import logging
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from sqlalchemy import text, select, func
from difflib import SequenceMatcher

# プロジェクトルートパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.db.connection import init_db, get_session_maker
from app.models import TalentScore, Talent

# マッピング辞書をインポート
try:
    from scripts.talent_name_mapping_dictionary import MANUAL_NAME_MAPPING, get_manual_mapping, get_alternative_names
except ImportError:
    # フォールバック辞書（マッピングファイルが見つからない場合）
    MANUAL_NAME_MAPPING = {
        "イチロー": "鈴木一朗（イチロー）",
        "ヒカキン": "HIKAKIN",
    }
    def get_manual_mapping(csv_name: str) -> str:
        return MANUAL_NAME_MAPPING.get(csv_name)
    def get_alternative_names(csv_name: str) -> list:
        return []

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f'tpr_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# TPRファイルと対応するターゲット層ID（修正版：診断システム実装に合わせて9-16を使用）
TPR_FILES_MAPPING = {
    "TPR_男性12～19_202508.csv": 9,   # 修正: 13 → 9 (男性12-19歳)
    "TPR_女性12～19_202508.csv": 10,  # 修正: 9 → 10 (女性12-19歳)
    "TPR_男性20～34_202508.csv": 11,  # 修正: 14 → 11 (男性20-34歳)
    "TPR_女性20～34_202508.csv": 12,  # 修正: 10 → 12 (女性20-34歳)
    "TPR_男性35～49_202508.csv": 13,  # 修正: 15 → 13 (男性35-49歳)
    "TPR_女性35～49_202508.csv": 14,  # 修正: 11 → 14 (女性35-49歳)
    "TPR_男性50～69_202508.csv": 15,  # 修正: 16 → 15 (男性50-69歳)
    "TPR_女性50～69_202508.csv": 16,  # 修正: 12 → 16 (女性50-69歳)
}

# CSVディレクトリパス
CSV_DIR = Path("/Users/lennon/projects/talent-casting-form/DBdata/【TPR】G列のパワースコアを採用する想定です")


class TPRImporter:
    def __init__(self):
        self.talent_map = {}
        self.matched_count = 0
        self.unmatched_count = 0
        self.unmatched_list = []
        self.fuzzy_matches = []

    async def load_talent_mapping(self):
        """データベースからタレント名マッピングを読み込み"""
        logger.info("📋 Loading talent name mapping from database...")

        async with get_session_maker()() as session:
            result = await session.execute(
                select(Talent.account_id, Talent.name_full_for_matching)
                .where(Talent.del_flag == 0)
            )

            for row in result.all():
                if row.name_full_for_matching:
                    # 完全一致用
                    self.talent_map[row.name_full_for_matching.strip()] = row.account_id

        logger.info(f"✅ Loaded {len(self.talent_map)} talent names")

    def normalize_name(self, name):
        """名前の正規化（マッチング精度向上のため）"""
        import re

        # 基本正規化
        normalized = name.strip()

        # 括弧とその中身を除去（コンビ名対応）
        normalized = re.sub(r'[（(][^）)]*[）)]', '', normalized)

        # スペース・ピリオド・記号を除去
        normalized = re.sub(r'[.\s　・!?]', '', normalized)

        # 全角英数を半角に変換
        normalized = normalized.translate(str.maketrans(
            'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９',
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        ))

        # 大文字に統一（英字の場合）
        normalized = normalized.upper()

        return normalized

    def find_best_match(self, csv_name, threshold=0.75):
        """改善されたあいまいマッチング（マッピング辞書統合版）"""
        csv_name = csv_name.strip()

        # 0. 手動マッピング辞書を最優先でチェック
        manual_mapping = get_manual_mapping(csv_name)
        if manual_mapping and manual_mapping in self.talent_map:
            return self.talent_map[manual_mapping], "manual_mapping"

        # 1. 完全一致を最優先
        if csv_name in self.talent_map:
            return self.talent_map[csv_name], "exact"

        # 2. 代替候補名でのマッチング（カナ・英字変換など）
        alternative_names = get_alternative_names(csv_name)
        for alt_name in alternative_names:
            if alt_name in self.talent_map:
                return self.talent_map[alt_name], "alternative_mapping"

        # 3. 正規化名での完全一致
        normalized_csv = self.normalize_name(csv_name)
        for db_name in self.talent_map.keys():
            if normalized_csv == self.normalize_name(db_name):
                return self.talent_map[db_name], "normalized_exact"

        # 4. 括弧部分のみでマッチング（コンビ名など）
        import re
        bracket_match = re.search(r'[（(]([^）)]+)[）)]', csv_name)
        if bracket_match:
            bracket_content = bracket_match.group(1)
            for db_name in self.talent_map.keys():
                if bracket_content in db_name or self.normalize_name(bracket_content) == self.normalize_name(db_name):
                    return self.talent_map[db_name], "bracket_match"

        # 5. 括弧を除去した部分でマッチング（個人名）
        name_without_bracket = re.sub(r'[（(][^）)]*[）)]', '', csv_name).strip()
        if name_without_bracket != csv_name:
            for db_name in self.talent_map.keys():
                if name_without_bracket == db_name or self.normalize_name(name_without_bracket) == self.normalize_name(db_name):
                    return self.talent_map[db_name], "individual_match"

        # 6. あいまいマッチング（通常）
        best_match = None
        best_ratio = 0

        for db_name in self.talent_map.keys():
            # 元の名前でのマッチング
            ratio1 = SequenceMatcher(None, csv_name, db_name).ratio()
            # 正規化名でのマッチング
            ratio2 = SequenceMatcher(None, normalized_csv, self.normalize_name(db_name)).ratio()

            # より高いスコアを採用
            ratio = max(ratio1, ratio2)

            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = db_name

        if best_match:
            return self.talent_map[best_match], f"fuzzy_{best_ratio:.2f}"

        return None, "no_match"

    async def process_csv_file(self, csv_file, target_segment_id, dry_run=True):
        """単一CSVファイルを処理"""
        logger.info(f"📁 Processing: {csv_file.name}")

        try:
            # CSVファイル読み込み（UTF-8 BOM対応）
            df = pd.read_csv(csv_file, encoding='utf-8-sig')

            # 必須カラムの確認
            required_cols = ['タレント名', 'スコア']
            if not all(col in df.columns for col in required_cols):
                logger.error(f"❌ Required columns missing: {required_cols}")
                return 0

            # データクリーニング
            df = df.dropna(subset=['タレント名', 'スコア'])
            df['タレント名'] = df['タレント名'].astype(str).str.strip()
            df['スコア'] = pd.to_numeric(df['スコア'], errors='coerce')
            df = df.dropna(subset=['スコア'])

            logger.info(f"📊 Total records in CSV: {len(df)}")

            updated_records = []

            for idx, row in df.iterrows():
                talent_name = row['タレント名']
                power_score = float(row['スコア'])

                # 名前マッチング
                account_id, match_type = self.find_best_match(talent_name)

                if account_id:
                    self.matched_count += 1

                    if match_type.startswith("fuzzy"):
                        self.fuzzy_matches.append({
                            'csv_name': talent_name,
                            'db_name': [name for name, aid in self.talent_map.items() if aid == account_id][0],
                            'account_id': account_id,
                            'match_ratio': match_type,
                            'power_score': power_score,
                            'target_segment_id': target_segment_id,
                            'file': csv_file.name
                        })

                    updated_records.append({
                        'account_id': account_id,
                        'target_segment_id': target_segment_id,
                        'tpr_power_score': power_score,
                        'csv_name': talent_name,
                        'match_type': match_type
                    })

                else:
                    self.unmatched_count += 1
                    self.unmatched_list.append({
                        'csv_name': talent_name,
                        'csv_kana': row.get('タレント名(全角カナ)', ''),
                        'power_score': power_score,
                        'file': csv_file.name,
                        'target_segment': target_segment_id
                    })

            if not dry_run and updated_records:
                await self.update_database(updated_records, target_segment_id)

            logger.info(f"✅ {csv_file.name}: {len(updated_records)} matched, {len(df) - len(updated_records)} unmatched")
            return len(updated_records)

        except Exception as e:
            logger.error(f"❌ Error processing {csv_file.name}: {e}")
            return 0

    async def update_database(self, records, target_segment_id):
        """データベースを更新（生SQL使用）"""
        async with get_session_maker()() as session:
            try:
                for record in records:
                    account_id = record['account_id']
                    segment_id = record['target_segment_id']
                    tpr_score = Decimal(str(record['tpr_power_score']))

                    # 既存レコード確認（生SQLクエリ）
                    result = await session.execute(
                        text('''
                            SELECT account_id, vr_popularity, tpr_power_score
                            FROM talent_scores
                            WHERE account_id = :account_id
                              AND target_segment_id = :target_segment_id
                        '''),
                        {
                            'account_id': account_id,
                            'target_segment_id': segment_id
                        }
                    )
                    existing_record = result.fetchone()

                    if existing_record:
                        # 既存レコード更新
                        vr_val = existing_record[1] if existing_record[1] else Decimal('0')
                        new_base_power = (vr_val + tpr_score) / 2

                        await session.execute(
                            text('''
                                UPDATE talent_scores
                                SET tpr_power_score = :tpr_score,
                                    base_power_score = :base_power_score,
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE account_id = :account_id
                                  AND target_segment_id = :target_segment_id
                            '''),
                            {
                                'account_id': account_id,
                                'target_segment_id': segment_id,
                                'tpr_score': tpr_score,
                                'base_power_score': new_base_power
                            }
                        )

                    else:
                        # 新規レコード作成（VRデータがない場合）
                        new_base_power = (Decimal('0') + tpr_score) / 2

                        await session.execute(
                            text('''
                                INSERT INTO talent_scores
                                (account_id, target_segment_id, vr_popularity, tpr_power_score, base_power_score, created_at, updated_at)
                                VALUES (:account_id, :target_segment_id, NULL, :tpr_score, :base_power_score, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            '''),
                            {
                                'account_id': account_id,
                                'target_segment_id': segment_id,
                                'tpr_score': tpr_score,
                                'base_power_score': new_base_power
                            }
                        )

                await session.commit()
                logger.info(f"✅ Database updated: {len(records)} records")

            except Exception as e:
                await session.rollback()
                logger.error(f"❌ Database update failed: {e}")
                raise

    def generate_reports(self):
        """マッチング結果レポートを生成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 1. マッチング失敗レポート
        if self.unmatched_list:
            df_unmatched = pd.DataFrame(self.unmatched_list)
            unmatched_file = f"tpr_unmatched_{timestamp}.csv"
            df_unmatched.to_csv(unmatched_file, index=False, encoding='utf-8-sig')
            logger.warning(f"📄 Unmatched names report: {unmatched_file}")

            # 上位10件を表示
            logger.warning(f"⚠️ Top 10 unmatched names:")
            for i, item in enumerate(self.unmatched_list[:10], 1):
                logger.warning(f"   {i}. {item['csv_name']} (score: {item['power_score']}, file: {item['file']})")

        # 2. あいまいマッチングレポート
        if self.fuzzy_matches:
            df_fuzzy = pd.DataFrame(self.fuzzy_matches)
            fuzzy_file = f"tpr_fuzzy_matches_{timestamp}.csv"
            df_fuzzy.to_csv(fuzzy_file, index=False, encoding='utf-8-sig')
            logger.info(f"📄 Fuzzy matches report: {fuzzy_file}")

            # 上位5件を表示
            logger.info(f"🔍 Top 5 fuzzy matches:")
            for i, item in enumerate(self.fuzzy_matches[:5], 1):
                logger.info(f"   {i}. '{item['csv_name']}' → '{item['db_name']}' ({item['match_ratio']})")

        # 3. サマリー
        total_processed = self.matched_count + self.unmatched_count
        match_rate = (self.matched_count / total_processed * 100) if total_processed > 0 else 0

        logger.info(f"\n📊 Processing Summary:")
        logger.info(f"   Total processed: {total_processed}")
        logger.info(f"   Matched: {self.matched_count} ({match_rate:.1f}%)")
        logger.info(f"   Unmatched: {self.unmatched_count} ({100-match_rate:.1f}%)")
        logger.info(f"   Fuzzy matches: {len(self.fuzzy_matches)}")

    async def run(self, dry_run=True):
        """メイン実行処理"""
        logger.info("=" * 80)
        if dry_run:
            logger.info("🧪 TPR DATA UPDATE - DRY RUN MODE")
        else:
            logger.info("🚀 TPR DATA UPDATE - EXECUTE MODE")
        logger.info("=" * 80)

        await init_db()
        await self.load_talent_mapping()

        total_updated = 0

        # 各TPRファイルを処理
        for filename, target_segment_id in TPR_FILES_MAPPING.items():
            csv_file = CSV_DIR / filename

            if not csv_file.exists():
                logger.warning(f"⚠️ File not found: {filename}")
                continue

            updated_count = await self.process_csv_file(csv_file, target_segment_id, dry_run)
            total_updated += updated_count

        # レポート生成
        self.generate_reports()

        if dry_run:
            logger.info(f"\n🧪 DRY RUN COMPLETE: {total_updated} records would be updated")
        else:
            logger.info(f"\n✅ UPDATE COMPLETE: {total_updated} records updated")

        logger.info("=" * 80)

        return total_updated


async def main():
    parser = argparse.ArgumentParser(
        description='TPRパワースコア更新（名前マッチング対応版）'
    )
    parser.add_argument('--dry-run', action='store_true', help='ドライラン（検証のみ）')
    parser.add_argument('--execute', action='store_true', help='実際に更新実行')

    args = parser.parse_args()

    if not (args.dry_run or args.execute):
        logger.error("❌ --dry-run または --execute を指定してください")
        return

    if args.execute:
        print("\n⚠️ 実際にデータベースを更新します。")
        confirm = input("継続しますか？ (yes/no): ")
        if confirm.lower() != 'yes':
            logger.info("❌ 処理をキャンセルしました")
            return

    importer = TPRImporter()
    await importer.run(dry_run=args.dry_run)


if __name__ == "__main__":
    asyncio.run(main())