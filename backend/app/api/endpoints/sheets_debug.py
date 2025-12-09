"""Google Sheetsデバッグ用エンドポイント"""
from fastapi import APIRouter
import os
import base64
import json
from typing import Dict, Any

router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.get("/sheets-config")
async def get_sheets_config() -> Dict[str, Any]:
    """Google Sheets設定情報デバッグ"""

    # 環境変数チェック
    enable_sheets = os.environ.get('ENABLE_SHEETS_EXPORT')
    sheets_id = os.environ.get('GOOGLE_SHEETS_ID')
    base64_creds = os.environ.get('GOOGLE_SERVICE_ACCOUNT_BASE64')

    config = {
        "ENABLE_SHEETS_EXPORT": enable_sheets,
        "GOOGLE_SHEETS_ID": sheets_id,
        "GOOGLE_SERVICE_ACCOUNT_BASE64_present": bool(base64_creds),
        "GOOGLE_SERVICE_ACCOUNT_BASE64_length": len(base64_creds) if base64_creds else 0,
    }

    # Base64をデコードしてJSON構造確認（credentials情報は表示しない）
    if base64_creds:
        try:
            decoded = base64.b64decode(base64_creds).decode('utf-8')
            creds_data = json.loads(decoded)
            config["credentials_structure"] = {
                "type": creds_data.get("type"),
                "project_id": creds_data.get("project_id"),
                "client_email": creds_data.get("client_email"),
                "has_private_key": "private_key" in creds_data,
                "private_key_length": len(creds_data.get("private_key", ""))
            }
        except Exception as e:
            config["credentials_decode_error"] = str(e)

    return config


@router.get("/test-sheets-connection")
async def test_sheets_connection() -> Dict[str, Any]:
    """Google Sheets接続テスト"""

    try:
        from app.services.sheets_exporter import SheetsExporter

        # SheetsExporterインスタンス作成試行
        exporter = SheetsExporter()

        # 簡単なテストデータでGoogle Sheets接続テスト
        test_data = [
            {
                "タレント名": "テスト接続確認",
                "カテゴリー": "デバッグ",
                "VR人気度": 50.0,
                "TPRスコア": 50.0,
                "従来スコア": 50.0,
                "おもしろさ": 50,
                "清潔感": 50,
                "個性的な": 50,
                "信頼できる": 50,
                "かわいい": 50,
                "カッコいい": 50,
                "大人の魅力": 50,
                "従来順位": 1,
                "業種別イメージ": 0,
                "最終スコア": 50.0,
                "最終順位": 1
            }
        ]

        # Google Sheets書き込みテスト
        await exporter.export_to_sheets(
            data=test_data,
            metadata={
                "実施日時": "2025-12-08 23:00:00",
                "業種": "デバッグテスト",
                "ターゲット": "接続確認",
                "予算": "テスト",
                "起用目的": "Google Sheets接続確認テスト",
                "企業名": "デバッグ株式会社",
                "担当者": "システム管理者"
            }
        )

        return {
            "success": True,
            "message": "Google Sheets接続テスト成功",
            "sheets_url": f"https://docs.google.com/spreadsheets/d/{os.environ.get('GOOGLE_SHEETS_ID')}/edit"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }