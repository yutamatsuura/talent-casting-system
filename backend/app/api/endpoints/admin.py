"""管理画面用APIエンドポイント"""

from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.db.connection import get_db_session, get_asyncpg_connection
from app.models import FormSubmission, ButtonClick, DiagnosisResult
from pydantic import BaseModel

router = APIRouter()


# Pydantic models for booking links
class BookingLinkUpdate(BaseModel):
    booking_url: str

@router.get("/admin/form-submissions")
async def get_form_submissions(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """フォーム送信履歴取得API

    管理画面で使用するフォーム送信データをすべて取得します。
    """
    try:
        # フォーム送信データを新しい順で取得
        query = select(FormSubmission).order_by(FormSubmission.created_at.desc())
        result = await db.execute(query)
        form_submissions = result.scalars().all()

        # 辞書形式に変換
        submissions_data = []
        for submission in form_submissions:
            # ジャンルデータをJSONから配列に変換
            preferred_genres = None
            if hasattr(submission, 'preferred_genres') and submission.preferred_genres:
                import json
                try:
                    preferred_genres = json.loads(submission.preferred_genres)
                except:
                    preferred_genres = []

            submissions_data.append({
                "id": submission.id,
                "session_id": submission.session_id,
                "industry": submission.industry,
                "target_segment": submission.target_segment,
                "purpose": getattr(submission, 'purpose', None),
                "budget_range": submission.budget_range,
                "company_name": submission.company_name,
                "email": submission.email,
                "contact_name": submission.contact_name,
                "phone_number": submission.phone,
                "genre_preference": getattr(submission, 'genre_preference', None),
                "preferred_genres": preferred_genres,
                "created_at": submission.created_at.isoformat() + "Z",
            })

        return submissions_data

    except Exception as e:
        print(f"❌ フォーム送信データ取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"フォーム送信データ取得エラー: {str(e)}")


@router.get("/admin/button-clicks")
async def get_button_clicks(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """ボタンクリック履歴取得API

    管理画面で使用するボタンクリックデータをすべて取得します。
    """
    try:
        # ボタンクリックデータを新しい順で取得（FormSubmissionと結合してsession_idを取得）
        query = select(ButtonClick, FormSubmission.session_id).join(
            FormSubmission, ButtonClick.form_submission_id == FormSubmission.id
        ).order_by(ButtonClick.clicked_at.desc())
        result = await db.execute(query)
        button_clicks = result.all()

        # 辞書形式に変換
        clicks_data = []
        for click, session_id in button_clicks:
            clicks_data.append({
                "id": click.id,
                "session_id": session_id,
                "button_type": click.button_type,
                "button_text": click.button_text,
                "clicked_at": click.clicked_at.isoformat() + "Z",
            })

        return clicks_data

    except Exception as e:
        print(f"❌ ボタンクリックデータ取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"ボタンクリックデータ取得エラー: {str(e)}")


@router.get("/admin/statistics")
async def get_admin_statistics(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """管理画面用統計データ取得API

    フォーム送信数、ボタンクリック数、クリック率などの統計を取得します。
    """
    try:
        # フォーム送信総数
        form_submissions_query = select(FormSubmission)
        form_result = await db.execute(form_submissions_query)
        total_submissions = len(form_result.scalars().all())

        # カウンセリング予約ボタンクリック数（重複を除く）
        counseling_clicks_query = select(FormSubmission.session_id).join(
            ButtonClick, ButtonClick.form_submission_id == FormSubmission.id
        ).where(ButtonClick.button_type == "counseling_booking")
        click_result = await db.execute(counseling_clicks_query)
        unique_counseling_clicks = len(set(session_id for session_id in click_result.scalars().all()))

        # クリック率計算
        click_rate = (unique_counseling_clicks / total_submissions * 100) if total_submissions > 0 else 0

        # 今日の送信数
        today_query = text("""
            SELECT COUNT(*)
            FROM form_submissions
            WHERE DATE(created_at) = CURRENT_DATE
        """)
        today_result = await db.execute(today_query)
        today_submissions = today_result.scalar()

        # 今週の送信数
        this_week_query = text("""
            SELECT COUNT(*)
            FROM form_submissions
            WHERE created_at >= DATE_TRUNC('week', CURRENT_DATE)
        """)
        this_week_result = await db.execute(this_week_query)
        this_week_submissions = this_week_result.scalar()

        return {
            "total_submissions": total_submissions,
            "unique_counseling_clicks": unique_counseling_clicks,
            "click_rate": round(click_rate, 2),
            "today_submissions": today_submissions,
            "this_week_submissions": this_week_submissions,
            "generated_at": datetime.now().isoformat() + "Z",
        }

    except Exception as e:
        print(f"❌ 統計データ取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"統計データ取得エラー: {str(e)}")


@router.get("/admin/export/csv")
async def export_form_data_csv(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """CSVエクスポート用データ取得API

    フォーム送信データとボタンクリックデータを統合したCSV用データを取得します。
    """
    try:
        # フォーム送信データとボタンクリックデータを結合したクエリ
        query = text("""
            SELECT
                fs.id,
                fs.session_id,
                fs.industry,
                fs.target_segment,
                fs.purpose,
                fs.budget_range,
                fs.company_name,
                fs.email,
                fs.contact_name,
                fs.phone,
                fs.created_at,
                CASE
                    WHEN bc.session_id IS NOT NULL THEN 'あり'
                    ELSE 'なし'
                END as button_clicked,
                bc.clicked_at as button_clicked_at
            FROM form_submissions fs
            LEFT JOIN (
                SELECT DISTINCT ON (session_id) session_id, clicked_at
                FROM button_clicks
                WHERE button_type = 'counseling_booking'
                ORDER BY session_id, clicked_at DESC
            ) bc ON fs.session_id = bc.session_id
            ORDER BY fs.created_at DESC
        """)

        result = await db.execute(query)
        rows = result.fetchall()

        # 辞書形式に変換
        export_data = []
        for row in rows:
            export_data.append({
                "id": row.id,
                "session_id": row.session_id,
                "industry": row.industry,
                "target_segment": row.target_segment,
                "purpose": row.purpose,
                "budget_range": row.budget_range,
                "company_name": row.company_name,
                "email": row.email,
                "contact_name": row.contact_name,
                "phone_number": row.phone,
                "created_at": row.created_at.isoformat() + "Z",
                "button_clicked": row.button_clicked,
                "button_clicked_at": row.button_clicked_at.isoformat() + "Z" if row.button_clicked_at else "",
            })

        return export_data

    except Exception as e:
        print(f"❌ CSVエクスポートデータ取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"CSVエクスポートデータ取得エラー: {str(e)}")


@router.get("/admin/booking-links")
async def get_booking_links(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """業界別予約リンク取得API

    管理画面で使用する業界別予約リンクデータをすべて取得します。
    """
    try:
        # 業界別予約リンクデータを取得
        query = text("""
            SELECT id, industry_name, booking_url, created_at, updated_at
            FROM industry_booking_links
            ORDER BY industry_name
        """)
        result = await db.execute(query)
        booking_links = result.fetchall()

        # 辞書形式に変換
        links_data = []
        for link in booking_links:
            links_data.append({
                "id": link.id,
                "industry_name": link.industry_name,
                "booking_url": link.booking_url,
                "created_at": link.created_at.isoformat() + "Z",
                "updated_at": link.updated_at.isoformat() + "Z" if link.updated_at else None,
            })

        return links_data

    except Exception as e:
        print(f"❌ 業界別予約リンクデータ取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"業界別予約リンクデータ取得エラー: {str(e)}")


@router.put("/admin/booking-links/{industry_id}")
async def update_booking_link(
    industry_id: int,
    booking_link_data: BookingLinkUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """業界別予約リンク更新API

    指定された業界の予約リンクを更新します。
    """
    try:
        # 業界IDが存在するかチェック
        check_query = text("""
            SELECT id FROM industry_booking_links WHERE id = :industry_id
        """)
        check_result = await db.execute(check_query, {"industry_id": industry_id})
        if not check_result.fetchone():
            raise HTTPException(status_code=404, detail="指定された業界が見つかりません")

        # 予約リンクを更新
        update_query = text("""
            UPDATE industry_booking_links
            SET booking_url = :booking_url, updated_at = CURRENT_TIMESTAMP
            WHERE id = :industry_id
        """)
        await db.execute(update_query, {
            "booking_url": booking_link_data.booking_url,
            "industry_id": industry_id
        })
        await db.commit()

        # 更新されたデータを取得して返却
        select_query = text("""
            SELECT id, industry_name, booking_url, created_at, updated_at
            FROM industry_booking_links
            WHERE id = :industry_id
        """)
        result = await db.execute(select_query, {"industry_id": industry_id})
        updated_link = result.fetchone()

        return {
            "id": updated_link.id,
            "industry_name": updated_link.industry_name,
            "booking_url": updated_link.booking_url,
            "created_at": updated_link.created_at.isoformat() + "Z",
            "updated_at": updated_link.updated_at.isoformat() + "Z",
            "message": "予約リンクが正常に更新されました"
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"❌ 業界別予約リンク更新エラー: {e}")
        raise HTTPException(status_code=500, detail=f"業界別予約リンク更新エラー: {str(e)}")


@router.get("/booking-link/{industry_name}")
async def get_booking_link_by_industry(
    industry_name: str,
    db: AsyncSession = Depends(get_db_session)
):
    """業界名による予約リンク取得API

    診断結果ページで使用する、業界名による予約リンク取得エンドポイント。
    """
    try:
        # 業界名で予約リンクを取得
        query = text("""
            SELECT booking_url
            FROM industry_booking_links
            WHERE industry_name = :industry_name
        """)
        result = await db.execute(query, {"industry_name": industry_name})
        booking_link = result.fetchone()

        if not booking_link:
            # デフォルトリンクを返す
            return {
                "booking_url": "https://app.spirinc.com/t/W63rJQN01CTXR-FjsFaOr/as/8FtIxQriLEvZxYqBlbzib/confirm",
                "message": f"業界 '{industry_name}' の専用リンクが見つからないため、デフォルトリンクを返します"
            }

        return {
            "booking_url": booking_link.booking_url,
            "industry_name": industry_name
        }

    except Exception as e:
        print(f"❌ 業界別予約リンク取得エラー: {e}")
        # エラーの場合もデフォルトリンクを返す
        return {
            "booking_url": "https://app.spirinc.com/t/W63rJQN01CTXR-FjsFaOr/as/8FtIxQriLEvZxYqBlbzib/confirm",
            "message": f"エラーが発生したため、デフォルトリンクを返します: {str(e)}"
        }


@router.get("/admin/form-submissions/{submission_id}/diagnosis")
async def get_submission_diagnosis(
    submission_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """特定フォーム送信の診断結果30名取得API

    管理画面の詳細モーダル内で、指定されたフォーム送信に対応する
    診断結果タレント30名を取得します。

    Args:
        submission_id: フォーム送信ID

    Returns:
        診断結果タレント一覧（順位順）
    """
    try:
        # フォーム送信の存在確認
        submission_query = select(FormSubmission).where(FormSubmission.id == submission_id)
        submission_result = await db.execute(submission_query)
        submission = submission_result.scalar_one_or_none()

        if not submission:
            raise HTTPException(status_code=404, detail=f"フォーム送信ID {submission_id} が見つかりません")

        # 診断結果を取得（順位順）
        diagnosis_query = select(DiagnosisResult).where(
            DiagnosisResult.form_submission_id == submission_id
        ).order_by(DiagnosisResult.ranking)

        diagnosis_result = await db.execute(diagnosis_query)
        diagnosis_results = diagnosis_result.scalars().all()

        # 診断結果が存在しない場合
        if not diagnosis_results:
            return {
                "form_submission_id": submission_id,
                "diagnosis_results": [],
                "message": "この送信に対する診断結果がまだ記録されていません"
            }

        # レスポンス形式に変換（基本データ + 詳細データ追加）
        results_data = []
        for result in diagnosis_results:
            # 基本データ
            result_data = {
                "ranking": result.ranking,
                "talent_account_id": result.talent_account_id,
                "talent_name": result.talent_name,
                "talent_category": result.talent_category,
                "matching_score": float(result.matching_score),
                "created_at": result.created_at.isoformat() + "Z"
            }

            try:
                # タレントの基本スコアデータを取得
                basic_score_query = text("""
                    SELECT vr_popularity, tpr_power_score, base_power_score
                    FROM talent_scores
                    WHERE account_id = :account_id
                    LIMIT 1
                """)

                basic_score_result = await db.execute(
                    basic_score_query,
                    {"account_id": result.talent_account_id}
                )
                basic_score = basic_score_result.fetchone()

                if basic_score:
                    vr_pop = float(basic_score.vr_popularity) if basic_score.vr_popularity else 0
                    tpr_score = float(basic_score.tpr_power_score) if basic_score.tpr_power_score else 0
                    # base_power_scoreが正しく保存されていない場合は、リアルタイム計算する
                    if basic_score.base_power_score and basic_score.base_power_score != basic_score.vr_popularity:
                        # データベースに正しい値が保存されている場合はそれを使用
                        base_power = round(float(basic_score.base_power_score), 2)
                    else:
                        # データベースの値が不正な場合は、仕様通りリアルタイム計算
                        base_power = round((vr_pop + tpr_score) / 2, 2) if (vr_pop or tpr_score) else 0

                    result_data.update({
                        "vr_popularity": vr_pop,
                        "tpr_power_score": tpr_score,
                        "base_power_score": round(base_power, 2),
                    })
                else:
                    result_data.update({
                        "vr_popularity": 0,
                        "tpr_power_score": 0,
                        "base_power_score": 0,
                    })

                # イメージスコアとその他詳細データを取得
                additional_data = await get_additional_talent_data_for_csv(
                    db, result.talent_account_id, submission.target_segment
                )

                result_data.update({
                    "interesting_score": additional_data.get("image_funny", 0),
                    "clean_score": additional_data.get("image_clean", 0),
                    "unique_score": additional_data.get("image_unique", 0),
                    "trustworthy_score": additional_data.get("image_trustworthy", 0),
                    "cute_score": additional_data.get("image_cute", 0),
                    "cool_score": additional_data.get("image_cool", 0),
                    "mature_score": additional_data.get("image_mature", 0),
                    "previous_ranking": additional_data.get("previous_ranking", 0),
                    "industry_image_score": round(float(result.image_adjustment), 1) if result.image_adjustment else 0,
                })

            except Exception as e:
                print(f"⚠️ タレント詳細データ取得エラー (account_id: {result.talent_account_id}): {e}")
                # エラー時はデフォルト値
                result_data.update({
                    "vr_popularity": 0,
                    "tpr_power_score": 0,
                    "base_power_score": 0,
                    "interesting_score": 0,
                    "clean_score": 0,
                    "unique_score": 0,
                    "trustworthy_score": 0,
                    "cute_score": 0,
                    "cool_score": 0,
                    "mature_score": 0,
                    "previous_ranking": 0,
                    "industry_image_score": 0,
                })

            results_data.append(result_data)

        return {
            "form_submission_id": submission_id,
            "total_results": len(results_data),
            "diagnosis_results": results_data,
            "session_info": {
                "session_id": submission.session_id,
                "company_name": submission.company_name,
                "industry": submission.industry,
                "target_segment": submission.target_segment,
                "budget_range": submission.budget_range,
                "submitted_at": submission.created_at.isoformat() + "Z"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 診断結果取得エラー: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"診断結果の取得中にエラーが発生しました: {str(e)}"
        )


@router.get(
    "/submissions/{submission_id}/diagnosis-results-for-csv",
    response_model=Dict[str, Any],
    summary="Google Sheetsと同じデータソースによる診断結果取得（CSV用）"
)
async def get_diagnosis_results_for_csv(
    submission_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Google Sheetsエクスポートと同じデータソース（enhanced_matching_debug）を使用
    正確な16列データを取得してCSV出力に使用
    """
    try:
        # フォーム送信データを確認
        query = select(FormSubmission).where(FormSubmission.id == submission_id)
        result = await db.execute(query)
        submission = result.scalar_one_or_none()

        if not submission:
            raise HTTPException(
                status_code=404,
                detail=f"送信ID {submission_id} が見つかりません"
            )

        # enhanced_matching_debugと同じロジックでデータを取得
        from app.services.enhanced_matching_debug import EnhancedMatchingDebug

        # マッチングデバッガーを初期化
        debug_matcher = EnhancedMatchingDebug()

        # Google Sheetsと同じ詳細データを取得
        detailed_results = await debug_matcher.generate_complete_talent_analysis(
            industry=submission.industry,
            target_segments=[submission.target_segment],
            purpose=submission.usage_purpose,
            budget=submission.budget_range
        )

        return {
            "form_submission_id": submission_id,
            "total_results": len(detailed_results),
            "csv_export_data": detailed_results,  # Google Sheetsと同じ構造
            "session_info": {
                "session_id": submission.session_id,
                "company_name": submission.company_name,
                "industry": submission.industry,
                "target_segment": submission.target_segment,
                "budget_range": submission.budget_range,
                "submitted_at": submission.created_at.isoformat() + "Z"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ CSV用診断結果取得エラー: {e}")
        raise HTTPException(
            status_code=500,
            detail="CSV用診断結果取得中にエラーが発生しました"
        )


async def get_additional_talent_data_for_csv(
    db: AsyncSession,
    account_id: int,
    target_segment: str
) -> Dict[str, Any]:
    """
    CSVエクスポート用のタレント追加データ取得
    enhanced_matching_debug.pyと同じロジックでtalent_imagesデータを取得
    """
    try:
        # target_segment_idを取得
        segment_query = text("SELECT target_segment_id FROM target_segments WHERE segment_name = :segment_name")
        segment_result = await db.execute(segment_query, {"segment_name": target_segment})
        segment_row = segment_result.fetchone()

        if not segment_row:
            print(f"⚠️ ターゲットセグメント '{target_segment}' が見つかりません")
            return {}

        target_segment_id = segment_row.target_segment_id

        # メインクエリ: VR/TPRデータとイメージスコアを一括取得
        query = text("""
            SELECT
                ma.account_id,
                ma.act_genre,
                ts.vr_popularity,
                ts.tpr_power_score,
                ti.image_funny,
                ti.image_clean,
                ti.image_unique,
                ti.image_trustworthy,
                ti.image_cute,
                ti.image_cool,
                ti.image_mature
            FROM m_account ma
            LEFT JOIN talent_scores ts ON ma.account_id = ts.account_id
                AND ts.target_segment_id = :target_segment_id
            LEFT JOIN talent_images ti ON ma.account_id = ti.account_id
                AND ti.target_segment_id = :target_segment_id
            WHERE ma.account_id = :account_id
        """)

        result = await db.execute(query, {
            "target_segment_id": target_segment_id,
            "account_id": account_id
        })

        row = result.fetchone()

        if not row:
            print(f"⚠️ アカウントID {account_id} のデータが見つかりません")
            return {}

        # 従来順位計算用の基礎パワー得点を取得
        conventional_score = ((row.vr_popularity or 0) + (row.tpr_power_score or 0)) / 2

        # 従来順位を計算（簡易版：同じtarget_segmentでの従来スコア順位）
        ranking_query = text("""
            SELECT COUNT(*) + 1 as ranking
            FROM talent_scores ts
            WHERE ts.target_segment_id = :target_segment_id
            AND ((ts.vr_popularity + ts.tpr_power_score) / 2) > :conventional_score
        """)

        ranking_result = await db.execute(ranking_query, {
            "target_segment_id": target_segment_id,
            "conventional_score": conventional_score
        })

        ranking_row = ranking_result.fetchone()
        previous_ranking = ranking_row.ranking if ranking_row else 0

        return {
            "act_genre": row.act_genre,
            "vr_popularity": round(float(row.vr_popularity or 0), 1),
            "tpr_power_score": round(float(row.tpr_power_score or 0), 1),
            "image_funny": round(float(row.image_funny or 0), 1),
            "image_clean": round(float(row.image_clean or 0), 1),
            "image_unique": round(float(row.image_unique or 0), 1),
            "image_trustworthy": round(float(row.image_trustworthy or 0), 1),
            "image_cute": round(float(row.image_cute or 0), 1),
            "image_cool": round(float(row.image_cool or 0), 1),
            "image_mature": round(float(row.image_mature or 0), 1),
            "previous_ranking": previous_ranking
        }

    except Exception as e:
        print(f"❌ タレント追加データ取得エラー (account_id: {account_id}): {e}")
        return {}


