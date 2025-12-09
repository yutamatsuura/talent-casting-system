"""
管理者・開発者専用デバッグAPIエンドポイント
Google Sheetsエクスポート機能を含む
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import asyncio

from app.schemas.matching import MatchingFormData
from app.services.matching_logic_debug import MatchingLogicDebug
from app.services.sheets_exporter import SheetsExporter

router = APIRouter(prefix="/admin", tags=["管理者デバッグ"])

class SheetsExportRequest(BaseModel):
    """Google Sheetsエクスポート要求"""
    sheet_id: str = Field(..., description="Google Sheets ID")
    industry: str = Field(..., description="業種")
    target_segments: str = Field(..., description="ターゲット層")
    purpose: str = Field(..., description="起用目的")
    budget: str = Field(..., description="予算")
    export_immediately: bool = Field(default=True, description="即座にエクスポートするか")

class MatchingDebugResponse(BaseModel):
    """マッチングデバッグ結果"""
    status: str
    message: str
    debug_data: Optional[Dict[str, Any]] = None
    export_result: Optional[Dict[str, Any]] = None  # stringからAnyに変更
    sheet_url: Optional[str] = None

@router.get(
    "/test-env",
    summary="環境変数テスト",
    description="Google認証の環境変数をテスト"
)
async def test_environment():
    """環境変数テスト"""
    import os
    return {
        "GOOGLE_APPLICATION_CREDENTIALS": os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
        "file_exists": os.path.exists(os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')),
        "current_working_directory": os.getcwd()
    }

@router.get(
    "/test-sheets-api",
    summary="Google Sheets API接続テスト",
    description="実際のAPI接続をテスト"
)
async def test_sheets_api():
    """Google Sheets API接続テスト"""
    try:
        from app.services.sheets_exporter import SheetsExporter
        exporter = SheetsExporter()

        if exporter.service is None:
            return {
                "status": "error",
                "message": "Google Sheets API サービス初期化失敗",
                "credentials": exporter.credentials is not None
            }

        # 簡単なAPI呼び出しテスト（スプレッドシート情報取得）
        sheet_id = "1lRsdHKJr8qxjbunlo7y7vYnN-jP3qdlgIdH7j9KooJc"
        result = exporter.service.spreadsheets().get(spreadsheetId=sheet_id).execute()

        return {
            "status": "success",
            "message": "Google Sheets API接続成功",
            "spreadsheet_title": result.get('properties', {}).get('title', 'Unknown'),
            "sheet_count": len(result.get('sheets', []))
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"API接続エラー: {str(e)}"
        }

@router.post(
    "/export-matching-debug",
    response_model=MatchingDebugResponse,
    summary="マッチングロジック詳細データをGoogle Sheetsにエクスポート",
    description="開発・テスト専用。マッチングの各ステップ詳細をGoogle Sheetsに出力"
)
async def export_matching_debug(
    request: SheetsExportRequest,
    background_tasks: BackgroundTasks
) -> MatchingDebugResponse:
    """
    16列完全版マッチングロジックの詳細実行結果をGoogle Sheetsにエクスポート
    スクリーンショットと同じ構造でデータを出力

    **使用例:**
    ```
    POST /api/admin/export-matching-debug
    {
        "sheet_id": "1abc123...",
        "industry": "化粧品・ヘアケア・オーラルケア",
        "target_segments": "女性20-34歳",
        "purpose": "認知度向上",
        "budget": "1000万円～3000万円未満"
    }
    ```

    **注意:**
    - Google Sheets APIの認証設定が必要
    - 開発・テスト環境でのみ使用
    - 大量データの場合は処理時間がかかる可能性
    """
    try:
        # Google Sheets API設定チェック（修正版）
        if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            raise HTTPException(
                status_code=500,
                detail="Google Sheets API認証情報が設定されていません"
            )

        # 完全版マッチングロジック実行
        from app.services.enhanced_matching_debug import EnhancedMatchingDebug
        enhanced_logic = EnhancedMatchingDebug()

        final_results, debug_data = await enhanced_logic.generate_complete_talent_analysis(
            industry=request.industry,
            target_segments=[request.target_segments],  # Convert single string to list
            purpose=request.purpose,
            budget=request.budget
        )

        # 入力条件をdebug_dataに追加
        debug_data["result_url"] = f"/results?industry={request.industry}"

        response_data = {
            "status": "success",
            "message": "16列完全版マッチングロジック実行完了",
            "debug_data": {
                "input_conditions": debug_data,
                "final_results": final_results,
                "step_calculations": []  # 簡略化
            }
        }

        # Google Sheetsエクスポート実行
        if request.export_immediately:
            sheets_exporter = SheetsExporter()

            export_result = await sheets_exporter.export_matching_debug(
                sheet_id=request.sheet_id,
                input_conditions=debug_data,
                step_calculations=[],  # 簡略化
                final_results=final_results
            )

            response_data["export_result"] = export_result
            response_data["sheet_url"] = export_result.get("sheet_url")

            if export_result["status"] == "error":
                response_data["status"] = "partial_success"
                response_data["message"] = f"マッチング実行成功、エクスポートエラー: {export_result['message']}"
        else:
            # バックグラウンドでエクスポート実行
            background_tasks.add_task(
                background_export_task,
                request.sheet_id,
                debug_data
            )
            response_data["message"] = "マッチングロジック実行完了、バックグラウンドでエクスポート中"

        return MatchingDebugResponse(**response_data)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"処理エラー: {str(e)}"
        )

@router.get(
    "/test-sheets-connection",
    summary="Google Sheets接続テスト",
    description="Google Sheets APIの接続確認用エンドポイント"
)
async def test_sheets_connection():
    """Google Sheets API接続テスト"""
    try:
        sheets_exporter = SheetsExporter()

        if not sheets_exporter.service:
            return {
                "status": "error",
                "message": "Google Sheets APIサービスが初期化されていません",
                "auth_configured": bool(os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON'))
            }

        return {
            "status": "success",
            "message": "Google Sheets API接続正常",
            "auth_configured": True,
            "service_available": True
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"接続エラー: {str(e)}",
            "auth_configured": bool(os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON'))
        }

@router.post(
    "/matching-test",
    summary="マッチングロジックテスト実行",
    description="Google Sheetsエクスポートなしでマッチングロジックのみテスト"
)
async def test_matching_logic(request: MatchingFormData):
    """マッチングロジックのみをテスト実行（エクスポートなし）"""
    try:
        matching_logic = MatchingLogicDebug()

        final_results, debug_data = await matching_logic.execute_matching_with_debug(
            industry=request.industry,
            target_segments=[request.target_segments],  # Convert single string to list
            purpose=request.purpose,
            budget=request.budget
        )

        return {
            "status": "success",
            "message": "マッチングロジックテスト完了",
            "summary": debug_data["summary"],
            "step_count": len(debug_data["step_calculations"]),
            "final_results_count": len(final_results),
            "top_3_results": final_results[:3]  # 上位3件のみ返却
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"マッチングテストエラー: {str(e)}"
        )

async def background_export_task(sheet_id: str, debug_data: Dict[str, Any]):
    """バックグラウンドでのGoogle Sheetsエクスポート処理"""
    try:
        sheets_exporter = SheetsExporter()

        export_result = await sheets_exporter.export_matching_debug(
            sheet_id=sheet_id,
            input_conditions=debug_data["input_conditions"],
            step_calculations=debug_data["step_calculations"],
            final_results=debug_data["final_results"]
        )

        print(f"バックグラウンドエクスポート完了: {export_result}")

    except Exception as e:
        print(f"バックグラウンドエクスポートエラー: {e}")

# 管理者認証用の簡易ミドルウェア（将来拡張用）
class AdminAuthMiddleware:
    """管理者認証ミドルウェア（現在は無効化、将来用）"""

    @staticmethod
    def verify_admin_token(token: str) -> bool:
        """管理者トークン検証（現在は常にTrue）"""
        # 将来的にJWTトークンや環境変数ベースの認証を実装
        return True