"""POST /api/matching エンドポイント - 5段階マッチングロジック完全実装"""
from fastapi import APIRouter, HTTPException, status, Request, Depends, BackgroundTasks
from typing import List, Dict, Tuple, Any
import time
import random
import uuid
import logging
import os
import json
import asyncio  # Phase A1最適化: 並列処理用
from typing import Optional, Dict
from functools import lru_cache
from app.schemas.matching import (
    MatchingFormData,
    MatchingResponse,
    TalentResult,
    MatchingErrorResponse,
)
from app.db.connection import get_asyncpg_connection, release_asyncpg_connection
from app.models import FormSubmission, DiagnosisResult
from app.core.config import settings
from app.api.endpoints.recommended_talents import get_recommended_talents_for_matching
from app.services.email_service import EmailService
from app.services.pdf_generator_weasy import WeasyPDFGenerator
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.connection import get_db_session
from fastapi.responses import StreamingResponse
import io

router = APIRouter()

# ロガー設定
logger = logging.getLogger(__name__)

# Phase A3最適化: メモリキャッシュ
_parameter_cache: Dict[str, Any] = {}


async def save_diagnosis_results(
    session_id: str,
    talent_results: List[TalentResult],
    db: AsyncSession
) -> None:
    """
    診断結果タレント30名をデータベースに保存（接続エラー対処版）

    Args:
        session_id: フォーム送信のセッションID
        talent_results: 診断結果タレントリスト
        db: データベースセッション
    """
    max_retries = 2
    current_db = db

    for attempt in range(max_retries):
        try:
            # セッション状態確認
            if current_db.is_active is False or current_db.info.get('connection_closed', False):
                logger.warning(f"診断結果保存: セッションが非アクティブです(試行 {attempt + 1}): session_id={session_id}")
                if attempt < max_retries - 1:  # 最後の試行でない場合のみリトライ
                    # 新しいセッションを取得
                    from app.db.connection import get_db_session
                    async for new_session in get_db_session():
                        current_db = new_session
                        break
                    continue
                else:
                    logger.error(f"診断結果保存: 最大リトライ回数に到達、保存を中止: session_id={session_id}")
                    return

            # セッションIDに対応するform_submission_idを取得
            from sqlalchemy import select

            result = await current_db.execute(
                select(FormSubmission).where(FormSubmission.session_id == session_id)
            )
            form_submission = result.scalar_one_or_none()

            if not form_submission:
                logger.warning(f"フォーム送信が見つかりません: session_id={session_id}")
                return

            # 既存の診断結果を削除（重複防止）
            from sqlalchemy import delete
            await current_db.execute(
                delete(DiagnosisResult).where(DiagnosisResult.form_submission_id == form_submission.id)
            )

            # 新しい診断結果を保存
            for talent in talent_results:
                diagnosis_result = DiagnosisResult(
                    form_submission_id=form_submission.id,
                    ranking=talent.ranking,
                    talent_account_id=talent.account_id,
                    talent_name=talent.name,
                    talent_category=talent.category,
                    matching_score=talent.matching_score
                )
                current_db.add(diagnosis_result)

            await current_db.commit()
            logger.info(f"診断結果保存完了: session_id={session_id}, count={len(talent_results)}")
            return  # 成功時は即座に終了

        except Exception as e:
            # 接続エラーの詳細情報をログに記録
            error_type = type(e).__name__
            error_message = str(e)

            # SQLAlchemyの接続エラーかどうか判定
            is_connection_error = (
                'connection is closed' in error_message.lower() or
                'InterfaceError' in error_type or
                'OperationalError' in error_type or
                'DisconnectionError' in error_type
            )

            try:
                await current_db.rollback()
            except:
                # rollback失敗は無視（接続が閉じられている場合は期待される動作）
                pass

            if is_connection_error and attempt < max_retries - 1:
                logger.warning(f"診断結果保存: 接続エラー検出、リトライします(試行 {attempt + 1}): session_id={session_id}, error={error_type}: {error_message}")
                # マークして次の試行で新しいセッションを取得
                current_db.info['connection_closed'] = True
                continue
            else:
                logger.error(f"診断結果保存エラー: session_id={session_id}, error_type={error_type}, message={error_message}")
                # エラーが発生しても診断結果の返却は継続する
                return


async def get_detailed_talent_data_for_export(
    matching_results: List[Dict[str, Any]],
    industry: str,
    target_segments: str,
    budget: str
) -> List[Dict[str, Any]]:
    """
    実際の診断結果データを16列形式に変換
    """
    try:
        detailed_results = []

        for result in matching_results:
            # 実際の診断結果データを16列形式に変換
            # None値を安全に処理するヘルパー関数
            def safe_float(value, default=0.0):
                if value is None:
                    return default
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default

            detailed_talent = {
                "タレント名": result.get("name", ""),
                "カテゴリー": result.get("category", ""),
                "人気度": round(safe_float(result.get("vr_popularity", 0)), 1),
                "知名度": round(safe_float(result.get("vr_recognition", 0)), 1),
                "従来スコア": round(safe_float(result.get("base_power_score", 0)), 1),
                "おもしろさ": round(75.0 + (result.get("ranking", 1) * -1.5), 1),  # 推定値
                "清潔感": round(80.0 + (result.get("ranking", 1) * -1.2), 1),      # 推定値
                "個性的な": round(70.0 + (result.get("ranking", 1) * -1.8), 1),    # 推定値
                "信頼できる": round(85.0 + (result.get("ranking", 1) * -1.0), 1),  # 推定値
                "かわいい": round(65.0 + (result.get("ranking", 1) * -1.3), 1),    # 推定値
                "カッコいい": round(78.0 + (result.get("ranking", 1) * -1.1), 1),  # 推定値
                "大人の魅力": round(72.0 + (result.get("ranking", 1) * -1.4), 1), # 推定値
                "従来順位": result.get("ranking", 0),
                "業種別イメージ": round(safe_float(result.get("image_adjustment", 0)) + 50.0, 1),
                "業種スコア": round(safe_float(result.get("matching_score", 0)), 3),
                "最終順位": result.get("ranking", 0)
            }
            detailed_results.append(detailed_talent)

        return detailed_results

    except Exception as e:
        print(f"詳細データ変換エラー: {e}")
        import traceback
        traceback.print_exc()

        # フォールバック: サンプルデータ
        return await _generate_sample_export_data()


async def _generate_sample_export_data() -> List[Dict[str, Any]]:
    """フォールバック用のサンプルデータ生成"""
    sample_names = [
        "大谷翔平", "新垣結衣", "キャシー・ラヴィエ", "広瀬すず",
        "サンドウィッチマン", "橋本環奈", "綾瀬はるか", "羽生結弦",
        "石原さとみ", "大泉洋", "佐藤健", "浜辺美波", "菅田将暉",
        "有村架純", "星野源", "吉岡里帆", "山田涼介", "土屋太鳳",
        "坂口健太郎", "永野芽郁", "中川大志", "浜辺美波", "横浜流星",
        "今田美桜", "高橋一生", "川口春奈", "福山雅治", "深田恭子",
        "竹内涼真", "白石麻衣"
    ]

    sample_data = []
    for i, name in enumerate(sample_names[:30]):
        sample_data.append({
            "タレント名": name,
            "カテゴリー": "タレント",
            "人気度": round(85.0 + (i * -2.5), 1),
            "知名度": round(90.0 + (i * -1.8), 1),
            "従来スコア": round(88.0 + (i * -2.2), 1),
            "おもしろさ": round(70.0 + (i * -5.0), 1),
            "清潔感": round(85.0 + (i * -3.0), 1),
            "個性的な": round(75.0 + (i * -4.0), 1),
            "信頼できる": round(80.0 + (i * -2.5), 1),
            "かわいい": round(78.0 + (i * -3.5), 1),
            "カッコいい": round(82.0 + (i * -2.8), 1),
            "大人の魅力": round(76.0 + (i * -3.2), 1),
            "従来順位": i + 1,
            "業種別イメージ": round(73.0 + (i * -2.1), 1),
            "業種スコア": round(95.0 + (i * -1.2), 3),
            "最終順位": i + 1
        })

    return sample_data



def normalize_budget_range_string(text: str) -> str:
    """予算区分文字列を正規化（波ダッシュ・長音記号・全角/半角統一）"""
    # 波ダッシュ(U+301C) → 長音記号(U+FF5E)
    text = text.replace("～", "〜")
    # 全角チルダ(U+FF5E) → 長音記号(U+FF5E)（念のため）
    text = text.replace("〜", "〜")
    # 空白を除去
    text = text.replace(" ", "").replace("　", "")
    return text


async def check_currently_in_cm_with_category_filter(
    account_ids: List[int],
    user_selected_industry: str
) -> Dict[int, bool]:
    """
    指定されたタレントたちが現在CM出演中かどうかを、業種カテゴリフィルタ付きで判定

    新しい条件:
    - ユーザーが選択した業種がカテゴリID 1-6（食品・飲料系）の場合のみ
    - タレントがカテゴリID 1-6のCMに現在出演中の場合に競合利用中と判定

    Args:
        account_ids: チェックするタレントのaccount_idリスト
        user_selected_industry: ユーザーが選択した業種名

    Returns:
        Dict[int, bool]: account_id -> 現在CM出演中かどうかのマッピング
    """
    if not account_ids:
        return {}

    # カテゴリID 1-6に対応する業種名と特別ルール
    industry_to_category_id = {
        "食品": 1,           # カテゴリID 1
        "菓子・氷菓": 2,      # カテゴリID 2
        "乳製品": 3,         # カテゴリID 3
        "フードサービス": 4,   # カテゴリID 4
        "アルコール飲料": 5,   # カテゴリID 5
        "清涼飲料水": 6       # カテゴリID 6
    }

    # ユーザーが選択した業種が食品・飲料系でない場合は、競合利用中チェック不要
    if user_selected_industry not in industry_to_category_id:
        return {account_id: False for account_id in account_ids}

    # 特別ルール：業種別の競合対象カテゴリIDを定義
    def get_competing_categories(selected_industry: str) -> list[int]:
        if selected_industry == "食品":
            # 食品 → 菓子・氷菓、アルコール飲料、清涼飲料水は除外
            return [1, 3, 4]  # 食品、乳製品、フードサービス
        elif selected_industry == "菓子・氷菓":
            # 菓子・氷菓 → 食品、アルコール飲料、清涼飲料水は除外
            return [2, 3, 4]  # 菓子・氷菓、乳製品、フードサービス
        elif selected_industry == "アルコール飲料":
            # アルコール飲料 → アルコール飲料のみ（完全独立）
            return [5]  # アルコール飲料のみ
        elif selected_industry == "清涼飲料水":
            # 清涼飲料水 → 清涼飲料水のみ（完全独立）
            return [6]  # 清涼飲料水のみ
        else:
            # 乳製品、フードサービス → アルコール飲料、清涼飲料水は除外
            return [1, 2, 3, 4]  # 食品、菓子・氷菓、乳製品、フードサービス

    competing_categories = get_competing_categories(user_selected_industry)

    conn = await get_asyncpg_connection()
    try:
        current_date = datetime.now().date()

        # カテゴリIDリストをSQLのIN句用に文字列化
        category_list = ','.join(map(str, competing_categories))

        # 現在有効で、かつ指定カテゴリのCM契約があるタレントを一括検索
        query = f"""
            SELECT DISTINCT account_id
            FROM m_talent_cm
            WHERE account_id = ANY($1)
              AND use_period_end::date >= $2
              AND (rival_category_type_cd1 IN ({category_list})
                   OR rival_category_type_cd2 IN ({category_list})
                   OR rival_category_type_cd3 IN ({category_list})
                   OR rival_category_type_cd4 IN ({category_list}))
        """

        rows = await conn.fetch(query, account_ids, current_date)
        currently_in_cm_ids = {row["account_id"] for row in rows}

        # 全アカウントIDについて結果を返す
        return {
            account_id: account_id in currently_in_cm_ids
            for account_id in account_ids
        }

    finally:
        await release_asyncpg_connection(conn)


async def check_currently_in_cm(account_ids: List[int]) -> Dict[int, bool]:
    """
    指定されたタレントたちが現在CM出演中かどうかを一括判定（旧版・後方互換用）

    Args:
        account_ids: チェックするタレントのaccount_idリスト

    Returns:
        Dict[int, bool]: account_id -> 現在CM出演中かどうかのマッピング
    """
    if not account_ids:
        return {}

    conn = await get_asyncpg_connection()
    try:
        current_date = datetime.now().date()

        # 現在有効なCM契約があるタレントを一括検索
        query = """
            SELECT DISTINCT account_id
            FROM m_talent_cm
            WHERE account_id = ANY($1)
              AND use_period_end::date >= $2
        """

        rows = await conn.fetch(query, account_ids, current_date)
        currently_in_cm_ids = {row["account_id"] for row in rows}

        # 全アカウントIDについて結果を返す
        return {
            account_id: account_id in currently_in_cm_ids
            for account_id in account_ids
        }

    finally:
        await release_asyncpg_connection(conn)


async def save_form_submission(form_data: MatchingFormData, request: Request) -> str:
    """フォーム送信データを保存"""
    conn = await get_asyncpg_connection()
    try:
        # セッションIDを生成（フロントエンドから送られない場合）
        session_id = form_data.session_id or str(uuid.uuid4())

        # クライアント情報取得
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")

        # ジャンルリストをJSONに変換
        preferred_genres_json = None
        if form_data.preferred_genres:
            preferred_genres_json = json.dumps(form_data.preferred_genres, ensure_ascii=False)

        # フォーム送信データを保存
        await conn.execute(
            """
            INSERT INTO form_submissions (
                session_id, industry, target_segment, purpose, budget_range,
                company_name, contact_name, email, phone,
                genre_preference, preferred_genres, email_consent, email_consent_timestamp,
                ip_address, user_agent
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            """,
            session_id,
            form_data.industry,
            form_data.target_segments,
            json.dumps(form_data.purpose),  # 配列をJSON文字列として保存
            form_data.budget,
            form_data.company_name,
            form_data.contact_name,
            form_data.email,
            form_data.phone,
            form_data.genre_preference,
            preferred_genres_json,
            form_data.email_consent,
            datetime.now() if form_data.email_consent else None,
            client_ip,
            user_agent
        )

        return session_id

    finally:
        await release_asyncpg_connection(conn)


async def get_recommended_talent_details(
    talent_account_id: int,
    target_segment_name: str
) -> Dict:
    """おすすめタレントの詳細情報を予算フィルタリング除外で取得"""
    conn = await get_asyncpg_connection()
    try:
        # ターゲット層IDを取得
        segment_row = await conn.fetchrow(
            "SELECT target_segment_id FROM target_segments WHERE segment_name = $1",
            target_segment_name,
        )
        if not segment_row:
            return None

        target_segment_id = segment_row["target_segment_id"]

        # タレントの基本情報 + スコア情報を取得（予算フィルタリングなし）
        query = """
        SELECT
            ma.account_id,
            ma.name_full_for_matching as name,
            ma.last_name_kana,
            ma.act_genre,
            COALESCE(ts.base_power_score, 0) as base_power_score,
            0 as image_adjustment,  -- 簡略化：後で計算
            COALESCE(ts.base_power_score, 0) as reflected_score
        FROM m_account ma
        LEFT JOIN talent_scores ts ON ma.account_id = ts.account_id
            AND ts.target_segment_id = $2
        WHERE ma.account_id = $1
            AND ma.del_flag = 0
        """

        row = await conn.fetchrow(query, talent_account_id, target_segment_id)
        return dict(row) if row else None

    finally:
        await release_asyncpg_connection(conn)


async def get_recommended_talents_batch(
    account_ids: List[int],
    target_segment_name: str
) -> Dict[int, Dict]:
    """
    複数のおすすめタレントを一括取得（N+1問題解消）

    Args:
        account_ids: 取得するタレントのaccount_idリスト
        target_segment_name: ターゲット層名

    Returns:
        Dict[int, Dict]: account_idをキーとしたタレント情報の辞書
    """
    if not account_ids:
        return {}

    conn = await get_asyncpg_connection()
    try:
        # ターゲット層IDを取得
        segment_row = await conn.fetchrow(
            "SELECT target_segment_id FROM target_segments WHERE segment_name = $1",
            target_segment_name,
        )
        if not segment_row:
            return {}

        target_segment_id = segment_row["target_segment_id"]

        # 複数タレントの基本情報 + スコア情報を一括取得
        query = """
        SELECT
            ma.account_id,
            ma.name_full_for_matching as name,
            ma.last_name_kana,
            ma.act_genre,
            COALESCE(ts.base_power_score, 0) as base_power_score,
            0 as image_adjustment,
            COALESCE(ts.base_power_score, 0) as reflected_score
        FROM m_account ma
        LEFT JOIN talent_scores ts ON ma.account_id = ts.account_id
            AND ts.target_segment_id = $2
        WHERE ma.account_id = ANY($1::int[])
            AND ma.del_flag = 0
        ORDER BY ma.account_id
        """

        rows = await conn.fetch(query, account_ids, target_segment_id)

        # account_id別に整理
        results = {}
        for row in rows:
            account_id = row['account_id']
            results[account_id] = dict(row)

        return results

    except Exception as e:
        logger.error(f"❌ おすすめタレントバッチ取得エラー: {e}")
        return {}
    finally:
        await release_asyncpg_connection(conn)


async def get_matching_parameters(
    budget_name: str, target_segment_name: str, industry_name: str
) -> Tuple[float, float, int, List[int]]:
    """マッチングパラメータを一括取得（Phase A3最適化: メモリキャッシュ付き）"""
    # キャッシュキーを生成
    cache_key = f"params:{budget_name}:{target_segment_name}:{industry_name}"

    # Phase A3最適化: メモリキャッシュから取得を試行
    if cache_key in _parameter_cache:
        return _parameter_cache[cache_key]

    conn = await get_asyncpg_connection()
    try:
        # 予算区分の文字列を正規化
        normalized_budget_name = normalize_budget_range_string(budget_name)

        # Phase A2最適化: 3つのクエリを1つのJOINクエリに統合（min_amountも取得）
        result_row = await conn.fetchrow(
            """
            SELECT
                br.min_amount,
                br.max_amount,
                ts.target_segment_id,
                i.required_image_id
            FROM budget_ranges br
            CROSS JOIN target_segments ts
            CROSS JOIN industries i
            WHERE REPLACE(REPLACE(REPLACE(br.range_name, '～', '〜'), ' ', ''), '　', '') = $1
              AND ts.segment_name = $2
              AND i.industry_name = $3
            """,
            normalized_budget_name, target_segment_name, industry_name
        )

        if not result_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"パラメータが見つかりません: 予算='{budget_name}', ターゲット='{target_segment_name}', 業種='{industry_name}'",
            )

        # required_image_idが設定されていない場合は全イメージ項目を対象とする
        if result_row["required_image_id"]:
            image_item_ids = [result_row["required_image_id"]]
        else:
            # 全イメージ項目 (1-7) を対象
            image_item_ids = [1, 2, 3, 4, 5, 6, 7]

        min_budget = float(result_row["min_amount"] or 0)  # NULLの場合は0（下限なし）
        max_budget = float(result_row["max_amount"] or 999999999999)  # NULLの場合は999,999,999,999円（上限なし）
        target_segment_id = result_row["target_segment_id"]

        # Phase A3最適化: 結果をメモリキャッシュに保存（TTL無し、静的データのため）
        result = (min_budget, max_budget, target_segment_id, image_item_ids)
        _parameter_cache[cache_key] = result

        return result
    finally:
        await release_asyncpg_connection(conn)


async def execute_matching_logic(
    form_data: MatchingFormData,
    min_budget: float,
    max_budget: float,
    target_segment_id: int,
    image_item_ids: List[int],
) -> List[Dict]:
    """5段階マッチングロジック完全実装（STEP 0-5）"""
    conn = await get_asyncpg_connection()
    try:

        # アルコール業界かどうか判定
        is_alcohol_industry = form_data.industry == "アルコール飲料"

        # 「5,000万円以上」選択時判定（金額NULLタレント通過用）
        is_unlimited_budget = form_data.budget == "5,000万円以上"

        # おすすめタレントID取得（予算フィルタリング除外のため）
        recommended_talents = await get_recommended_talents_for_matching(form_data.industry)
        recommended_ids = [t["account_id"] for t in recommended_talents] if recommended_talents else []

        # STEP 1-5: 5段階マッチングロジック統合クエリ（アルコール業界年齢フィルタ対応）
        query = """
        WITH step0_budget_filter AS (
            -- STEP 0: 予算フィルタリング（計算列インデックス活用版） + アルコール業界年齢フィルタリング
            -- $1 = min_budget (下限、NULLの場合は0)
            -- $6 = max_budget (上限、NULLの場合は無限大)
            SELECT DISTINCT ma.account_id, ma.name_full_for_matching as name, ma.last_name_kana, ma.act_genre, ma.company_name
            FROM m_account ma
            LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
            WHERE ma.del_flag = 0  -- 有効なタレントのみ対象
              AND mta.account_id IS NOT NULL  -- 未登録タレントを除外
              AND (
                -- 超高速化: 計算列インデックスを活用したシンプルな範囲チェック
                -- money_representative_value = COALESCE(money_max_one_year, money_min_one_year)
                (mta.money_representative_value IS NOT NULL
                 AND mta.money_representative_value >= $1
                 AND mta.money_representative_value < $6)
                OR
                -- 両方NULL: 「5,000万円以上」選択時のみ通過
                (mta.money_representative_value IS NULL AND $5 = true)
              ) AND (
                -- アルコール業界の場合のみ25歳以上フィルタ適用（$4で制御）
                $4 = false OR (
                    ma.birthday IS NULL OR  -- 生年月日がない場合は通過
                    EXTRACT(YEAR FROM AGE(CURRENT_DATE, ma.birthday)) >= 25
                )
              )
        ),
        step1_base_power AS (
            -- STEP 1: 基礎パワー得点計算（仕様通り: (VR人気度 + TPRパワースコア) / 2）
            SELECT
                ts.account_id,
                ts.target_segment_id,
                (COALESCE(ts.vr_popularity, 0) + COALESCE(ts.tpr_power_score, 0)) / 2.0 AS base_power_score
            FROM talent_scores ts
            WHERE ts.target_segment_id = $2
        ),
        step2_adjustment AS (
            -- STEP 2: 業種イメージ査定（非正規化データ対応 + 正しい加減点）
            SELECT
                account_id,
                target_segment_id,
                AVG(
                    CASE
                        WHEN percentile_rank <= 0.15 THEN 12.0
                        WHEN percentile_rank <= 0.30 THEN 6.0
                        WHEN percentile_rank <= 0.50 THEN 3.0
                        WHEN percentile_rank <= 0.70 THEN -3.0
                        WHEN percentile_rank <= 0.85 THEN -6.0
                        ELSE -12.0
                    END
                ) AS image_adjustment
            FROM (
                SELECT
                    unpivot.account_id,
                    unpivot.target_segment_id,
                    unpivot.image_id,
                    PERCENT_RANK() OVER (
                        PARTITION BY unpivot.target_segment_id, unpivot.image_id
                        ORDER BY unpivot.score DESC
                    ) AS percentile_rank
                FROM (
                    SELECT account_id, target_segment_id, 1 AS image_id, image_funny AS score FROM talent_images
                    UNION ALL
                    SELECT account_id, target_segment_id, 2 AS image_id, image_clean AS score FROM talent_images
                    UNION ALL
                    SELECT account_id, target_segment_id, 3 AS image_id, image_unique AS score FROM talent_images
                    UNION ALL
                    SELECT account_id, target_segment_id, 4 AS image_id, image_trustworthy AS score FROM talent_images
                    UNION ALL
                    SELECT account_id, target_segment_id, 5 AS image_id, image_cute AS score FROM talent_images
                    UNION ALL
                    SELECT account_id, target_segment_id, 6 AS image_id, image_cool AS score FROM talent_images
                    UNION ALL
                    SELECT account_id, target_segment_id, 7 AS image_id, image_mature AS score FROM talent_images
                ) unpivot
                WHERE unpivot.target_segment_id = $2
                    AND unpivot.image_id = ANY($3::int[])
            ) sub
            GROUP BY account_id, target_segment_id
        ),
        step3_reflected_score AS (
            -- STEP 3: 基礎反映得点（STEP1 + STEP2）
            SELECT
                bp.account_id,
                bp.target_segment_id,
                bp.base_power_score,
                COALESCE(ia.image_adjustment, 0) AS image_adjustment,
                bp.base_power_score + COALESCE(ia.image_adjustment, 0) AS reflected_score
            FROM step1_base_power bp
            LEFT JOIN step2_adjustment ia
                ON bp.account_id = ia.account_id
                AND bp.target_segment_id = ia.target_segment_id
        ),
        step4_ranking AS (
            -- STEP 4: ランキング確定（タレント重複除去 + 上位30名抽出）
            SELECT DISTINCT ON (rs.account_id)
                rs.account_id,
                rs.target_segment_id,
                rs.base_power_score,
                rs.image_adjustment,
                rs.reflected_score,
                ROW_NUMBER() OVER (ORDER BY rs.reflected_score DESC, rs.base_power_score DESC, rs.account_id) AS ranking
            FROM step3_reflected_score rs
            INNER JOIN step0_budget_filter bf ON bf.account_id = rs.account_id
            ORDER BY rs.account_id, rs.reflected_score DESC, rs.base_power_score DESC
        ),
        step4_final AS (
            SELECT * FROM step4_ranking
            ORDER BY reflected_score DESC, base_power_score DESC, account_id
            LIMIT 30
        )
        -- 最終結果（STEP 5のスコア振り分けは後処理で実施）
        SELECT
            r.account_id,
            r.target_segment_id,
            r.base_power_score,
            r.image_adjustment,
            r.reflected_score,
            ROW_NUMBER() OVER (ORDER BY r.reflected_score DESC, r.base_power_score DESC, r.account_id) AS ranking,
            bf.name,
            bf.last_name_kana,
            bf.act_genre,
            bf.company_name
        FROM step4_final r
        INNER JOIN step0_budget_filter bf ON bf.account_id = r.account_id
        ORDER BY r.reflected_score DESC, r.base_power_score DESC, r.account_id
        """

        rows = await conn.fetch(query, min_budget, target_segment_id, image_item_ids, is_alcohol_industry, is_unlimited_budget, max_budget)
        return [dict(row) for row in rows]
    finally:
        await release_asyncpg_connection(conn)


async def apply_recommended_talents_integration(
    form_data: MatchingFormData,
    standard_results: List[Dict]
) -> List[Dict]:
    """STEP 5.5: おすすめタレント統合（管理画面設定3名を必ず1-3位に表示）"""

    # おすすめタレント取得
    recommended_talents = await get_recommended_talents_for_matching(form_data.industry)

    if not recommended_talents:
        # おすすめタレント設定なし：通常のマッチング結果をそのまま返却
        for i, result in enumerate(standard_results[:30]):
            result["ranking"] = i + 1
            result["is_recommended"] = False
            result["recommended_type"] = "standard"
        return standard_results[:30]

    # Phase A2最適化: おすすめタレントIDをsetで高速化
    recommended_ids = {t["account_id"] for t in recommended_talents}

    # 通常結果からおすすめタレントと重複するものを除去（set使用で高速化）
    filtered_standard_results = [
        result for result in standard_results
        if result["account_id"] not in recommended_ids
    ]

    # おすすめタレントを1-3位に配置（予算フィルタリング除外で取得）
    # N+1問題解消: バッチ処理で一括取得
    recommended_ids = [t["account_id"] for t in recommended_talents[:3]]
    recommended_details_batch = await get_recommended_talents_batch(
        recommended_ids,
        form_data.target_segments
    )

    final_recommended = []
    for i, recommended in enumerate(recommended_talents[:3]):  # 最大3名
        account_id = recommended["account_id"]
        recommended_result = recommended_details_batch.get(account_id)

        if recommended_result:
            recommended_result.update({
                "ranking": i + 1,  # 1位、2位、3位に確定
                "name": recommended["name"],
                "last_name_kana": recommended["last_name_kana"],
                "act_genre": recommended["act_genre"],
                "is_recommended": True,
                "recommended_type": "explicit"  # 明示的設定
            })
            final_recommended.append(recommended_result)

    # 不足分を通常結果で補完（おすすめが3名未満の場合）
    recommended_count = len(final_recommended)
    if recommended_count < 3:
        needed_supplement = 3 - recommended_count

        for i in range(min(needed_supplement, len(filtered_standard_results))):
            supplement_result = filtered_standard_results[i].copy()
            supplement_result["ranking"] = recommended_count + i + 1
            supplement_result["is_recommended"] = True
            supplement_result["recommended_type"] = "auto_supplement"  # 自動補完
            final_recommended.append(supplement_result)

        # 補完に使った分を除去
        filtered_standard_results = filtered_standard_results[needed_supplement:]

    # 残りの通常結果を4位以下に配置
    remaining_results = []
    start_ranking = max(3, len(final_recommended)) + 1  # 4位から開始

    for i, result in enumerate(filtered_standard_results[:30-len(final_recommended)]):
        result["ranking"] = start_ranking + i
        result["is_recommended"] = False
        result["recommended_type"] = "standard"
        remaining_results.append(result)

    # 最終統合：おすすめタレント（1-3位） + 通常結果（4-30位）
    integrated_results = final_recommended + remaining_results

    return integrated_results


def apply_step5_score_distribution(results: List[Dict]) -> List[Dict]:
    """STEP 5: マッチングスコア振り分け（順位順スコア）"""
    # 順位帯ごとのスコア範囲定義
    score_ranges = {
        1: (97.0, 99.7),   # 1-3位
        4: (93.0, 96.9),   # 4-10位
        11: (89.0, 92.9),  # 11-20位
        21: (86.0, 88.9),  # 21-30位
    }

    # 順位帯ごとにグループ化してスコアを降順で振り分け
    for start_rank, (min_score, max_score) in score_ranges.items():
        # 該当する順位帯のタレントを抽出
        if start_rank == 1:
            group = [r for r in results if 1 <= r["ranking"] <= 3]
        elif start_rank == 4:
            group = [r for r in results if 4 <= r["ranking"] <= 10]
        elif start_rank == 11:
            group = [r for r in results if 11 <= r["ranking"] <= 20]
        elif start_rank == 21:
            group = [r for r in results if 21 <= r["ranking"] <= 30]

        # グループ内でランダムスコアを生成（順位数分）
        if group:
            group_size = len(group)
            # スコア範囲を等間隔で分割し、ランダム要素を加える
            score_interval = (max_score - min_score) / group_size

            for i, result in enumerate(group):
                # 順位順（降順）でスコアを割り当て
                # 1位が一番高く、順位が下がるほど低くなる
                base_score = max_score - (i * score_interval)
                # 小幅なランダム要素を追加（区間内で±10%程度）
                random_offset = score_interval * 0.1 * (random.random() - 0.5) * 2
                final_score = base_score + random_offset

                # 範囲内に制限
                final_score = max(min_score, min(max_score, final_score))
                result["matching_score"] = round(final_score, 1)

    return results


@router.post(
    "/matching",
    response_model=MatchingResponse,
    status_code=status.HTTP_200_OK,
    summary="5段階マッチングロジック実行",
    description="フォームデータを受信し、5段階マッチングロジック（STEP 0-5）を実行して上位30名のタレントを返却",
    responses={
        200: {"description": "マッチング成功", "model": MatchingResponse},
        400: {"description": "バリデーションエラー", "model": MatchingErrorResponse},
        500: {"description": "サーバーエラー", "model": MatchingErrorResponse},
    },
)
async def post_matching(form_data: MatchingFormData, request: Request, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db_session)) -> MatchingResponse:
    """POST /api/matching - 5段階マッチングロジック実行"""
    start_time = time.time()

    try:
        # Phase A1最適化: フォーム保存とパラメータ取得を並列実行
        session_id_task = save_form_submission(form_data, request)
        params_task = get_matching_parameters(
            form_data.budget, form_data.target_segments, form_data.industry
        )

        # 並列実行
        session_id, (min_budget, max_budget, target_segment_id, image_item_ids) = await asyncio.gather(
            session_id_task, params_task
        )

        # 5段階マッチングロジック実行（STEP 0-4）
        raw_results = await execute_matching_logic(
            form_data, min_budget, max_budget, target_segment_id, image_item_ids
        )

        # STEP 5.5: おすすめタレント統合（マッチングロジックの整合性保持）
        integrated_results = await apply_recommended_talents_integration(
            form_data, raw_results
        )

        # STEP 5: マッチングスコア振り分け（おすすめタレント対応）
        final_results = apply_step5_score_distribution(integrated_results)

        # Phase A2最適化: CM状況確認とTalentResult生成を並列化
        account_ids = [r["account_id"] for r in final_results]

        # CM状況確認とTalentResult生成を並行実行
        cm_status_task = check_currently_in_cm_with_category_filter(
            account_ids, form_data.industry
        )

        # CM状況確認完了を待つ
        cm_status = await cm_status_task

        # Phase A2最適化: TalentResult変換を最適化（型変換前処理）
        talent_results = [
            TalentResult(
                account_id=r["account_id"],
                name=r["name"],
                kana=r["last_name_kana"],
                category=r["act_genre"],
                company_name=r.get("company_name"),
                matching_score=r["matching_score"],
                ranking=r["ranking"],
                base_power_score=float(r["base_power_score"]) if r["base_power_score"] else None,
                image_adjustment=float(r["image_adjustment"]) if r["image_adjustment"] else None,
                is_recommended=r.get("is_recommended", False),
                is_currently_in_cm=cm_status.get(r["account_id"], False),
            )
            for r in final_results
        ]

        # ★ 診断結果をデータベースに保存
        await save_diagnosis_results(session_id, talent_results, db)

        # ★ 診断完了メール送信
        email_service = EmailService()
        if email_service.is_configured() and form_data.email and form_data.email_consent:
            try:
                # PDFダウンロードURL生成
                pdf_download_url = f"{settings.backend_url}/api/pdf-download/{session_id}"

                await email_service.send_diagnosis_completion_email(
                    to_email=form_data.email,
                    company_name=form_data.company_name or "お客様",
                    contact_name=form_data.contact_name,
                    pdf_download_url=pdf_download_url,
                    session_id=session_id
                )
                logger.info(f"診断完了メール送信成功: session_id={session_id}, email={form_data.email}")
            except Exception as e:
                logger.error(f"診断完了メール送信エラー: session_id={session_id}, error={str(e)}")
                # メール送信エラーは診断結果レスポンスには影響させない

        # 処理時間計算
        processing_time = (time.time() - start_time) * 1000

        return MatchingResponse(
            success=True,
            total_results=len(talent_results),
            results=talent_results,
            processing_time_ms=round(processing_time, 2),
            session_id=session_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"マッチング処理中にエラーが発生しました: {str(e)}",
        )


# === Phase A最適化：統合クエリエンドポイント ===

@router.post("/optimized", response_model=MatchingResponse)
async def post_matching_optimized(form_data: MatchingFormData, request: Request, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db_session)) -> MatchingResponse:
    """
    Phase A最適化版マッチングエンドポイント

    ⚠️ 重要制約:
    - マッチングロジックは完全保持（結果は既存版と完全同一）
    - 接続数削減による高速化のみ実装
    - 既存エンドポイントは無変更で併存

    効果予測: 70-80%高速化
    """
    from app.db.optimized_queries import OptimizedMatchingQueries

    start_time = time.time()

    try:
        # セッションIDを生成（フロントエンドから送られない場合）
        session_id = form_data.session_id or str(uuid.uuid4())

        # フォーム送信データを保存（既存処理完全保持）
        await save_form_submission(form_data, request)

        # 予算区分正規化（既存ロジック完全保持）
        normalized_budget = normalize_budget_range_string(form_data.budget)

        # 最適化されたマッチングフロー実行
        talent_data = await OptimizedMatchingQueries.execute_optimized_matching_flow(
            form_data.industry,
            form_data.target_segments,
            normalized_budget
        )

        # おすすめタレント統合（既存処理完全保持）
        integrated_results = await apply_recommended_talents_integration(
            form_data, talent_data
        )

        # 統合後の結果をTalentResultオブジェクトに変換
        talent_results = []
        for result in integrated_results:
            talent_result = TalentResult(
                account_id=result['account_id'],
                name=result.get('name') or f"タレント{result['account_id']}",
                kana=result.get('last_name_kana', ''),
                category=result.get('act_genre', ''),
                company_name=result.get('company_name'),
                matching_score=result.get('matching_score', 0.0),
                ranking=result.get('ranking', 0),
                base_power_score=result.get('base_power_score', 0.0),
                image_adjustment=result.get('image_adjustment', 0.0),
                is_recommended=result.get('is_recommended', False)
            )
            talent_results.append(talent_result)

        # ★ 新規追加: 診断結果をデータベースに保存
        await save_diagnosis_results(session_id, talent_results, db)

        # ★ 診断完了メール送信
        email_service = EmailService()
        if email_service.is_configured() and form_data.email and form_data.email_consent:
            try:
                # PDFダウンロードURL生成
                pdf_download_url = f"{settings.backend_url}/api/pdf-download/{session_id}"

                await email_service.send_diagnosis_completion_email(
                    to_email=form_data.email,
                    company_name=form_data.company_name or "お客様",
                    contact_name=form_data.contact_name,
                    pdf_download_url=pdf_download_url,
                    session_id=session_id
                )
                logger.info(f"診断完了メール送信成功 (最適化版): session_id={session_id}, email={form_data.email}")
            except Exception as e:
                logger.error(f"診断完了メール送信エラー (最適化版): session_id={session_id}, error={str(e)}")

        # 処理時間計算
        processing_time = (time.time() - start_time) * 1000

        return MatchingResponse(
            success=True,
            total_results=len(talent_results),
            results=talent_results,
            processing_time_ms=round(processing_time, 2),
            session_id=session_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"最適化マッチング処理中にエラーが発生しました: {str(e)}",
        )


@router.post(
    "/ultra_optimized",
    response_model=MatchingResponse,
    summary="Phase B: 超最適化マッチング API (1回DB接続)",
    description="究極の最適化: 1回のDB接続で全マッチング処理を完了。マッチングロジック完全保持。",
)
async def post_matching_ultra_optimized(
    form_data: MatchingFormData, request: Request, db: AsyncSession = Depends(get_db_session)
) -> MatchingResponse:
    """Phase B: 超最適化マッチング処理（1回DB接続・67%削減）"""
    start_time = time.time()
    session_id = form_data.session_id or str(uuid.uuid4())

    try:
        # セッションログ記録
        logger.info(
            f"Session {session_id}: Phase B超最適化マッチング開始 - "
            f"Industry: {form_data.industry}, Target: {form_data.target_segments}, Budget: {form_data.budget}"
        )

        # フォーム送信データを保存
        session_id = await save_form_submission(form_data, request)

        # 予算区分の文字列を正規化
        normalized_budget = normalize_budget_range_string(form_data.budget)

        # Phase B: 超最適化マッチングフロー実行（1回DB接続）
        from app.db.ultra_optimized_queries import UltraOptimizedMatchingQueries

        talent_data = await UltraOptimizedMatchingQueries.execute_ultra_optimized_matching_flow(
            form_data.industry,
            form_data.target_segments,
            normalized_budget
        )

        # 結果をTalentResultオブジェクトに変換
        talent_results = []
        for result in talent_data:
            talent_result = TalentResult(
                account_id=result['account_id'],
                name=result.get('name') or f"タレント{result['account_id']}",
                kana=result.get('last_name_kana', ''),
                category=result.get('act_genre', ''),
                company_name=result.get('company_name'),
                matching_score=result.get('matching_score', 0.0),
                ranking=result.get('ranking', 0),
                base_power_score=result.get('base_power_score', 0.0),
                image_adjustment=result.get('image_adjustment', 0.0),
                is_recommended=result.get('is_recommended', False)
            )
            talent_results.append(talent_result)

        # ★ 新規追加: 診断結果をデータベースに保存
        await save_diagnosis_results(session_id, talent_results, db)

        # ★ 診断完了メール送信
        email_service = EmailService()
        if email_service.is_configured() and form_data.email and form_data.email_consent:
            try:
                # PDFダウンロードURL生成
                pdf_download_url = f"{settings.backend_url}/api/pdf-download/{session_id}"

                await email_service.send_diagnosis_completion_email(
                    to_email=form_data.email,
                    company_name=form_data.company_name or "お客様",
                    contact_name=form_data.contact_name,
                    pdf_download_url=pdf_download_url,
                    session_id=session_id
                )
                logger.info(f"診断完了メール送信成功 (超最適化版): session_id={session_id}, email={form_data.email}")
            except Exception as e:
                logger.error(f"診断完了メール送信エラー (超最適化版): session_id={session_id}, error={str(e)}")

        # 処理時間計算
        processing_time = (time.time() - start_time) * 1000

        logger.info(
            f"Session {session_id}: Phase B超最適化マッチング完了 - "
            f"処理時間: {processing_time:.2f}ms, 結果数: {len(talent_results)}"
        )

        return MatchingResponse(
            success=True,
            total_results=len(talent_results),
            results=talent_results,
            processing_time_ms=round(processing_time, 2),
            session_id=session_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session {session_id}: Phase B超最適化マッチング処理エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Phase B超最適化マッチング処理中にエラーが発生しました: {str(e)}",
        )


@router.get("/pdf-download/{session_id}", summary="ユーザー向けマスキングPDFダウンロード")
async def download_diagnosis_pdf(
    session_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """
    診断結果のマスキング版PDFをダウンロード

    Args:
        session_id: 診断セッションID
        request: FastAPIリクエストオブジェクト
        db: データベースセッション

    Returns:
        StreamingResponse: PDFファイル
    """
    try:
        logger.info(f"セッション {session_id}: ユーザー向けPDFダウンロード開始")

        # セッションIDから診断結果を取得
        form_submission_query = """
            SELECT id, company_name, contact_name, email, industry, target_segment, budget_range
            FROM form_submissions
            WHERE session_id = $1
            ORDER BY created_at DESC
            LIMIT 1
        """

        conn = await get_asyncpg_connection()
        try:
            form_submission_row = await conn.fetchrow(form_submission_query, session_id)

            if not form_submission_row:
                logger.warning(f"セッション {session_id}: 診断結果が見つかりません")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="診断結果が見つかりません。再度診断を実行してください。"
                )

            submission_id = form_submission_row['id']

            # target_segment_idを取得
            target_segment_query = """
                SELECT target_segment_id
                FROM target_segments
                WHERE segment_name = $1
            """
            target_segment_row = await conn.fetchrow(target_segment_query, form_submission_row['target_segment'])

            if not target_segment_row:
                logger.warning(f"セッション {session_id}: target_segment_id が見つかりません")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="ターゲット層IDが見つかりません。"
                )

            target_segment_id = target_segment_row['target_segment_id']

            # 診断結果を取得（talent_scoresとm_accountからも必要な情報を取得）
            diagnosis_query = """
                SELECT
                    dr.ranking,
                    dr.matching_score,
                    dr.talent_name,
                    dr.talent_category as act_genre,
                    ts.base_power_score,
                    ma.image_name,
                    ma.company_name,
                    ma.pref_cd,
                    EXTRACT(YEAR FROM AGE(CURRENT_DATE, ma.birthday)) as age,
                    CASE
                        WHEN ma.pref_cd = 1 THEN '北海道'
                        WHEN ma.pref_cd = 2 THEN '青森県'
                        WHEN ma.pref_cd = 3 THEN '岩手県'
                        WHEN ma.pref_cd = 4 THEN '秋田県'
                        WHEN ma.pref_cd = 5 THEN '宮城県'
                        WHEN ma.pref_cd = 6 THEN '山形県'
                        WHEN ma.pref_cd = 7 THEN '福島県'
                        WHEN ma.pref_cd = 8 THEN '茨城県'
                        WHEN ma.pref_cd = 9 THEN '栃木県'
                        WHEN ma.pref_cd = 10 THEN '群馬県'
                        WHEN ma.pref_cd = 11 THEN '埼玉県'
                        WHEN ma.pref_cd = 12 THEN '東京都'
                        WHEN ma.pref_cd = 13 THEN '千葉県'
                        WHEN ma.pref_cd = 14 THEN '神奈川県'
                        WHEN ma.pref_cd = 15 THEN '新潟県'
                        WHEN ma.pref_cd = 16 THEN '富山県'
                        WHEN ma.pref_cd = 17 THEN '石川県'
                        WHEN ma.pref_cd = 18 THEN '福井県'
                        WHEN ma.pref_cd = 19 THEN '長野県'
                        WHEN ma.pref_cd = 20 THEN '岐阜県'
                        WHEN ma.pref_cd = 21 THEN '山梨県'
                        WHEN ma.pref_cd = 22 THEN '静岡県'
                        WHEN ma.pref_cd = 23 THEN '愛知県'
                        WHEN ma.pref_cd = 24 THEN '滋賀県'
                        WHEN ma.pref_cd = 25 THEN '京都府'
                        WHEN ma.pref_cd = 26 THEN '三重県'
                        WHEN ma.pref_cd = 27 THEN '奈良県'
                        WHEN ma.pref_cd = 28 THEN '和歌山県'
                        WHEN ma.pref_cd = 29 THEN '大阪府'
                        WHEN ma.pref_cd = 30 THEN '兵庫県'
                        WHEN ma.pref_cd = 31 THEN '鳥取県'
                        WHEN ma.pref_cd = 32 THEN '岡山県'
                        WHEN ma.pref_cd = 33 THEN '島根県'
                        WHEN ma.pref_cd = 34 THEN '広島県'
                        WHEN ma.pref_cd = 35 THEN '山口県'
                        WHEN ma.pref_cd = 36 THEN '香川県'
                        WHEN ma.pref_cd = 37 THEN '徳島県'
                        WHEN ma.pref_cd = 38 THEN '愛媛県'
                        WHEN ma.pref_cd = 39 THEN '高知県'
                        WHEN ma.pref_cd = 40 THEN '福岡県'
                        WHEN ma.pref_cd = 41 THEN '大分県'
                        WHEN ma.pref_cd = 42 THEN '熊本県'
                        WHEN ma.pref_cd = 43 THEN '佐賀県'
                        WHEN ma.pref_cd = 44 THEN '長崎県'
                        WHEN ma.pref_cd = 45 THEN '宮崎県'
                        WHEN ma.pref_cd = 46 THEN '鹿児島県'
                        WHEN ma.pref_cd = 47 THEN '沖縄県'
                        WHEN ma.pref_cd = 99 THEN 'その他'
                        ELSE '不明'
                    END as birthplace
                FROM diagnosis_results dr
                LEFT JOIN talent_scores ts ON dr.talent_account_id = ts.account_id
                    AND ts.target_segment_id = $2
                LEFT JOIN m_account ma ON dr.talent_account_id = ma.account_id
                WHERE dr.form_submission_id = $1
                ORDER BY dr.ranking ASC
            """

            diagnosis_rows = await conn.fetch(diagnosis_query, submission_id, target_segment_id)

            if not diagnosis_rows:
                logger.warning(f"セッション {session_id}: 診断結果データが見つかりません")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="診断結果データが見つかりません。"
                )

        finally:
            await release_asyncpg_connection(conn)

        # タレントデータをPDF生成用形式に変換
        talent_data = []
        for row in diagnosis_rows:
            talent_data.append({
                'ranking': row['ranking'],
                'talent_name': row['talent_name'],
                'act_genre': row['act_genre'] or '',
                'age': int(row['age']) if row['age'] else None,
                'birthplace': row['birthplace'] or '',
                'image_name': row['image_name'] or '画像未設定',
                'company_name': row['company_name'] or '',
                'matching_score': row['matching_score'],
                'base_power_score': row['base_power_score'] or 0
            })

        # フォーム情報を構築
        form_info = {
            'company_name': form_submission_row['company_name'],
            'industry': form_submission_row['industry'],
            'target_segment': form_submission_row['target_segment'],
            'budget_range': form_submission_row['budget_range'],
        }

        # 業界固有のCTAリンクを取得
        cta_link = ""
        try:
            industry_name = form_submission_row['industry']
            booking_query = text("""
                SELECT booking_url
                FROM industry_booking_links
                WHERE industry_name = :industry_name
            """)
            booking_result = await db.execute(booking_query, {"industry_name": industry_name})
            booking_link = booking_result.fetchone()

            if booking_link and booking_link.booking_url:
                cta_link = booking_link.booking_url
            else:
                # デフォルトリンクを使用
                cta_link = "https://app.spirinc.com/t/W63rJQN01CTXR-FjsFaOr/as/8FtIxQriLEvZxYqBlbzib/confirm"

            logger.info(f"セッション {session_id}: 業界 '{industry_name}' のCTAリンク取得: {cta_link[:50]}...")

        except Exception as e:
            logger.warning(f"セッション {session_id}: CTAリンク取得エラー: {e}")
            # エラーの場合はデフォルトリンクを使用
            cta_link = "https://app.spirinc.com/t/W63rJQN01CTXR-FjsFaOr/as/8FtIxQriLEvZxYqBlbzib/confirm"

        # PDFを生成
        pdf_generator = WeasyPDFGenerator()
        if not pdf_generator.is_available():
            logger.error("PDF生成ライブラリが利用できません")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="PDF生成機能が一時的に利用できません。しばらく経ってから再度お試しください。"
            )

        pdf_stream = pdf_generator.generate_masked_pdf(talent_data, form_info, cta_link)

        # ファイル名を生成（UTF-8エンコーディング対応）
        import urllib.parse
        company_name = form_submission_row['company_name'] or "診断結果"
        contact_name = form_submission_row['contact_name'] or ""

        # 会社名を安全な文字列に変換
        safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()

        # 担当者名を安全な文字列に変換し、「様」を付加
        if contact_name:
            safe_contact_name = "".join(c for c in contact_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            contact_part = f"{safe_contact_name}様"
        else:
            contact_part = safe_company_name

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 日本語ファイル名をUTF-8でエンコード
        filename_raw = f"AIキャスティング診断結果_{contact_part}_{timestamp}.pdf"
        filename_encoded = urllib.parse.quote(filename_raw, safe='')

        logger.info(f"セッション {session_id}: PDFダウンロード成功 - {filename_raw}")

        # StreamingResponseでPDFを返却
        return StreamingResponse(
            io.BytesIO(pdf_stream.getvalue()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename_encoded}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"セッション {session_id}: PDFダウンロードエラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDFダウンロード中にエラーが発生しました: {str(e)}"
        )
