"""管理画面用APIエンドポイント"""

from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.db.connection import get_db_session
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

        # レスポンス形式に変換（詳細データ付き）
        results_data = []
        for result in diagnosis_results:
            # タレントの詳細データを取得
            talent_detail_query = text("""
                SELECT
                    ts.vr_popularity,
                    ts.tpr_power_score,
                    ts.base_power_score,
                    t.talent_name,
                    t.talent_category,
                    -- イメージスコア取得（最新のターゲット層で）
                    (SELECT ti.score FROM talent_images ti
                     INNER JOIN image_items ii ON ti.image_item_id = ii.id
                     WHERE ti.account_id = :account_id AND ii.image_name = 'おもしろい'
                     ORDER BY ti.created_at DESC LIMIT 1) as interesting_score,
                    (SELECT ti.score FROM talent_images ti
                     INNER JOIN image_items ii ON ti.image_item_id = ii.id
                     WHERE ti.account_id = :account_id AND ii.image_name = '清潔感がある'
                     ORDER BY ti.created_at DESC LIMIT 1) as clean_score,
                    (SELECT ti.score FROM talent_images ti
                     INNER JOIN image_items ii ON ti.image_item_id = ii.id
                     WHERE ti.account_id = :account_id AND ii.image_name = '個性的な'
                     ORDER BY ti.created_at DESC LIMIT 1) as unique_score,
                    (SELECT ti.score FROM talent_images ti
                     INNER JOIN image_items ii ON ti.image_item_id = ii.id
                     WHERE ti.account_id = :account_id AND ii.image_name = '信頼できる'
                     ORDER BY ti.created_at DESC LIMIT 1) as trustworthy_score,
                    (SELECT ti.score FROM talent_images ti
                     INNER JOIN image_items ii ON ti.image_item_id = ii.id
                     WHERE ti.account_id = :account_id AND ii.image_name = 'かわいい'
                     ORDER BY ti.created_at DESC LIMIT 1) as cute_score,
                    (SELECT ti.score FROM talent_images ti
                     INNER JOIN image_items ii ON ti.image_item_id = ii.id
                     WHERE ti.account_id = :account_id AND ii.image_name = 'カッコいい'
                     ORDER BY ti.created_at DESC LIMIT 1) as cool_score,
                    (SELECT ti.score FROM talent_images ti
                     INNER JOIN image_items ii ON ti.image_item_id = ii.id
                     WHERE ti.account_id = :account_id AND ii.image_name = '大人の魅力がある'
                     ORDER BY ti.created_at DESC LIMIT 1) as mature_score
                FROM talent_scores ts
                INNER JOIN m_account t ON ts.account_id = t.account_id
                WHERE ts.account_id = :account_id
                LIMIT 1
            """)

            talent_detail_result = await db.execute(
                talent_detail_query,
                {"account_id": result.talent_account_id}
            )
            talent_detail = talent_detail_result.fetchone()

            # 詳細データを含むレスポンス
            result_data = {
                "ranking": result.ranking,
                "talent_account_id": result.talent_account_id,
                "talent_name": result.talent_name,
                "talent_category": result.talent_category,
                "matching_score": float(result.matching_score),
                "created_at": result.created_at.isoformat() + "Z"
            }

            # 詳細データがある場合は追加
            if talent_detail:
                result_data.update({
                    "vr_popularity": float(talent_detail.vr_popularity) if talent_detail.vr_popularity else 0,
                    "tpr_power_score": float(talent_detail.tpr_power_score) if talent_detail.tpr_power_score else 0,
                    "base_power_score": float(talent_detail.base_power_score) if talent_detail.base_power_score else 0,
                    "interesting_score": float(talent_detail.interesting_score) if talent_detail.interesting_score else 0,
                    "clean_score": float(talent_detail.clean_score) if talent_detail.clean_score else 0,
                    "unique_score": float(talent_detail.unique_score) if talent_detail.unique_score else 0,
                    "trustworthy_score": float(talent_detail.trustworthy_score) if talent_detail.trustworthy_score else 0,
                    "cute_score": float(talent_detail.cute_score) if talent_detail.cute_score else 0,
                    "cool_score": float(talent_detail.cool_score) if talent_detail.cool_score else 0,
                    "mature_score": float(talent_detail.mature_score) if talent_detail.mature_score else 0,
                    "previous_ranking": 0,  # 従来順位は現在未実装
                    "industry_image_score": 0,  # 業種別イメージは現在未実装
                })
            else:
                # デフォルト値
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