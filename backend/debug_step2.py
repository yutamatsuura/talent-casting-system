#!/usr/bin/env python3
"""
STEP 2 業種イメージ査定の詳細調査
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from app.db.connection import init_db, get_session_maker
from sqlalchemy import text

async def investigate_step2_issue():
    """内村光良と日村勇紀のSTEP2加点問題を調査"""
    await init_db()
    session_maker = get_session_maker()

    print("=" * 80)
    print("🔍 STEP 2 業種イメージ査定バグ調査")
    print("=" * 80)

    async with session_maker() as session:

        # 1. テーブル構造確認
        print("\n【1】talent_imagesテーブル構造確認")
        print("-" * 50)

        result = await session.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'talent_images'
            ORDER BY ordinal_position
        """))

        print("talent_imagesテーブルのカラム:")
        for row in result.fetchall():
            print(f"  {row[0]} ({row[1]}) - NULL可: {row[2]}")

        # 2. 内村光良と日村勇紀のaccount_id確認
        print("\n【2】対象タレントのaccount_id確認")
        print("-" * 50)

        result = await session.execute(text("""
            SELECT account_id, name_full_for_matching
            FROM m_account
            WHERE name_full_for_matching LIKE '%内村%'
               OR name_full_for_matching LIKE '%日村%'
        """))

        talent_info = {}
        for row in result.fetchall():
            talent_info[row[1]] = row[0]
            print(f"{row[1]}: account_id = {row[0]}")

        # 3. 男性35-49歳のtarget_segment_id確認
        print("\n【3】男性35-49歳のtarget_segment_id確認")
        print("-" * 50)

        # target_segment_idの推定（TPRファイルマッピングから）
        target_segment_id = 13  # TPRファイルから推定：男性35-49歳
        print(f"target_segment_id（推定）: {target_segment_id} - 男性35-49歳")

        # 4. 食品業種のrequired_image_id確認
        print("\n【4】食品業種のrequired_image_id確認")
        print("-" * 50)

        result = await session.execute(text("""
            SELECT industry_id, industry_name, required_image_id
            FROM industries
            WHERE industry_name LIKE '%食品%'
        """))

        required_image_id = None
        for row in result.fetchall():
            required_image_id = row[2]
            print(f"industry_id: {row[0]} - {row[1]} - required_image_id: {row[2]}")

        # 5. 信頼できるのimage_item_id確認
        print("\n【5】信頼できるのimage_item_id確認")
        print("-" * 50)

        result = await session.execute(text("""
            SELECT id, code, name
            FROM image_items
            WHERE name LIKE '%信頼%' OR code LIKE '%trust%'
        """))

        trustworthy_image_id = None
        for row in result.fetchall():
            trustworthy_image_id = row[0]
            print(f"image_item_id: {row[0]} - {row[1]} - {row[2]}")

        # 6. 内村光良と日村勇紀の信頼スコア確認（実データ）
        if target_segment_id and len(talent_info) >= 2:
            print(f"\n【6】対象タレントの信頼スコア確認（target_segment_id: {target_segment_id}）")
            print("-" * 50)

            # まずテーブル構造を確認
            result = await session.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'talent_images'
                  AND column_name IN ('image_trustworthy', 'image_item_id', 'score')
            """))

            existing_columns = [row[0] for row in result.fetchall()]
            print(f"存在するカラム: {existing_columns}")

            if 'image_trustworthy' in existing_columns:
                # 非正規化形式
                print("\n🔍 非正規化形式でスコア確認:")
                result = await session.execute(text("""
                    SELECT ma.name_full_for_matching, ti.image_trustworthy
                    FROM talent_images ti
                    JOIN m_account ma ON ti.account_id = ma.account_id
                    WHERE ti.target_segment_id = :target_segment_id
                      AND ma.account_id IN :account_ids
                    ORDER BY ti.image_trustworthy DESC
                """), {
                    'target_segment_id': target_segment_id,
                    'account_ids': tuple(talent_info.values())
                })

                talent_scores = {}
                for row in result.fetchall():
                    talent_scores[row[0]] = row[1]
                    print(f"{row[0]}: 信頼スコア = {row[1]}")

            elif 'image_item_id' in existing_columns and 'score' in existing_columns:
                # 正規化形式
                print("\n🔍 正規化形式でスコア確認:")
                result = await session.execute(text("""
                    SELECT ma.name_full_for_matching, ti.score
                    FROM talent_images ti
                    JOIN m_account ma ON ti.account_id = ma.account_id
                    WHERE ti.target_segment_id = :target_segment_id
                      AND ti.image_item_id = :image_item_id
                      AND ma.account_id IN :account_ids
                    ORDER BY ti.score DESC
                """), {
                    'target_segment_id': target_segment_id,
                    'image_item_id': trustworthy_image_id or 4,
                    'account_ids': tuple(talent_info.values())
                })

                talent_scores = {}
                for row in result.fetchall():
                    talent_scores[row[0]] = row[1]
                    print(f"{row[0]}: 信頼スコア = {row[1]}")

            # 7. PERCENT_RANK実際の計算確認
            print(f"\n【7】PERCENT_RANK実際の計算確認（target_segment_id: {target_segment_id}）")
            print("-" * 50)

            if 'image_trustworthy' in existing_columns:
                # 非正規化形式での計算
                result = await session.execute(text("""
                    SELECT
                        ma.name_full_for_matching,
                        ti.image_trustworthy as score,
                        PERCENT_RANK() OVER (ORDER BY ti.image_trustworthy DESC) as percentile_rank_desc,
                        PERCENT_RANK() OVER (ORDER BY ti.image_trustworthy ASC) as percentile_rank_asc,
                        CASE
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.image_trustworthy DESC) <= 0.15 THEN 12.0
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.image_trustworthy DESC) <= 0.30 THEN 6.0
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.image_trustworthy DESC) <= 0.50 THEN 3.0
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.image_trustworthy DESC) <= 0.70 THEN -3.0
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.image_trustworthy DESC) <= 0.85 THEN -6.0
                            ELSE -12.0
                        END as expected_adjustment_desc,
                        CASE
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.image_trustworthy ASC) <= 0.15 THEN 12.0
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.image_trustworthy ASC) <= 0.30 THEN 6.0
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.image_trustworthy ASC) <= 0.50 THEN 3.0
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.image_trustworthy ASC) <= 0.70 THEN -3.0
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.image_trustworthy ASC) <= 0.85 THEN -6.0
                            ELSE -12.0
                        END as expected_adjustment_asc
                    FROM talent_images ti
                    JOIN m_account ma ON ti.account_id = ma.account_id
                    WHERE ti.target_segment_id = :target_segment_id
                      AND ma.account_id IN :account_ids
                    ORDER BY ti.image_trustworthy DESC
                """), {
                    'target_segment_id': target_segment_id,
                    'account_ids': tuple(talent_info.values())
                })

                print("タレント別PERCENT_RANK計算結果:")
                print("名前\t\tスコア\tパーセンタイル(DESC)\tパーセンタイル(ASC)\t期待加点(DESC)\t期待加点(ASC)")
                for row in result.fetchall():
                    print(f"{row[0]:<15}\t{row[1]:<6}\t{row[2]:<15.3f}\t{row[3]:<15.3f}\t{row[4]:<12}\t{row[5]}")

            elif 'image_item_id' in existing_columns and 'score' in existing_columns:
                # 正規化形式での計算
                result = await session.execute(text("""
                    SELECT
                        ma.name_full_for_matching,
                        ti.score,
                        PERCENT_RANK() OVER (ORDER BY ti.score DESC) as percentile_rank_desc,
                        PERCENT_RANK() OVER (ORDER BY ti.score ASC) as percentile_rank_asc,
                        CASE
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.score DESC) <= 0.15 THEN 12.0
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.score DESC) <= 0.30 THEN 6.0
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.score DESC) <= 0.50 THEN 3.0
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.score DESC) <= 0.70 THEN -3.0
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.score DESC) <= 0.85 THEN -6.0
                            ELSE -12.0
                        END as expected_adjustment_desc,
                        CASE
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.score ASC) <= 0.15 THEN 12.0
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.score ASC) <= 0.30 THEN 6.0
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.score ASC) <= 0.50 THEN 3.0
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.score ASC) <= 0.70 THEN -3.0
                            WHEN PERCENT_RANK() OVER (ORDER BY ti.score ASC) <= 0.85 THEN -6.0
                            ELSE -12.0
                        END as expected_adjustment_asc
                    FROM talent_images ti
                    JOIN m_account ma ON ti.account_id = ma.account_id
                    WHERE ti.target_segment_id = :target_segment_id
                      AND ti.image_item_id = :image_item_id
                      AND ma.account_id IN :account_ids
                    ORDER BY ti.score DESC
                """), {
                    'target_segment_id': target_segment_id,
                    'image_item_id': trustworthy_image_id or 4,
                    'account_ids': tuple(talent_info.values())
                })

                print("タレント別PERCENT_RANK計算結果:")
                print("名前\t\tスコア\tパーセンタイル(DESC)\tパーセンタイル(ASC)\t期待加点(DESC)\t期待加点(ASC)")
                for row in result.fetchall():
                    print(f"{row[0]:<15}\t{row[1]:<6}\t{row[2]:<15.3f}\t{row[3]:<15.3f}\t{row[4]:<12}\t{row[5]}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(investigate_step2_issue())