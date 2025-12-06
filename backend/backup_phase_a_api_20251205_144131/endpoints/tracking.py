"""ボタンクリック追跡エンドポイント"""
from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Optional
from app.db.connection import get_asyncpg_connection

router = APIRouter()


class ButtonClickData(BaseModel):
    """ボタンクリックデータスキーマ"""
    session_id: str = Field(..., min_length=1, description="セッションID")
    button_type: str = Field(..., min_length=1, description="ボタンタイプ")
    button_text: Optional[str] = Field(None, description="ボタンテキスト")


class ButtonClickResponse(BaseModel):
    """ボタンクリックレスポンススキーマ"""
    success: bool = Field(True, description="処理成功フラグ")
    message: str = Field(..., description="処理結果メッセージ")


@router.post(
    "/track-button-click",
    response_model=ButtonClickResponse,
    status_code=status.HTTP_200_OK,
    summary="ボタンクリック追跡",
    description="ボタンクリックを追跡してデータベースに記録",
)
async def track_button_click(click_data: ButtonClickData, request: Request) -> ButtonClickResponse:
    """POST /api/track-button-click - ボタンクリック追跡"""
    conn = await get_asyncpg_connection()
    try:
        # クライアント情報取得
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")

        # セッションIDが存在するかチェック
        form_submission = await conn.fetchrow(
            "SELECT id FROM form_submissions WHERE session_id = $1",
            click_data.session_id
        )

        if not form_submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"セッションID '{click_data.session_id}' が見つかりません"
            )

        # ボタンクリックデータを記録
        await conn.execute(
            """
            INSERT INTO button_clicks (
                form_submission_id, button_type, button_text,
                ip_address, user_agent
            ) VALUES ($1, $2, $3, $4, $5)
            """,
            form_submission["id"],
            click_data.button_type,
            click_data.button_text,
            client_ip,
            user_agent
        )

        return ButtonClickResponse(
            success=True,
            message="ボタンクリックが正常に記録されました"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ボタンクリック記録中にエラーが発生しました: {str(e)}"
        )
    finally:
        await conn.close()