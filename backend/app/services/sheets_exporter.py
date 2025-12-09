"""
Google Sheets API連携によるマッチングロジック検証用データエクスポート
開発・テスト専用機能
"""
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class SheetsExporter:
    def __init__(self):
        """Google Sheets API クライアント初期化"""
        # サービスアカウント認証情報の設定
        # 本番環境では環境変数から取得
        self.credentials = None
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Google Sheets APIサービスを初期化"""
        try:
            print(f"🔍 Google Sheets初期化開始...")
            start_time = time.time()
            # まずファイルパス方式を試す（ローカル環境用）
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            print(f"🔍 デバッグ: GOOGLE_APPLICATION_CREDENTIALS = {credentials_path}")

            if credentials_path and os.path.exists(credentials_path):
                print(f"🔍 デバッグ: ファイル方式で認証情報読み込み")
                self.credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                self.service = build('sheets', 'v4', credentials=self.credentials)
                print(f"✅ Google Sheets API初期化成功（ファイル方式）: {credentials_path}")
                return

            # Base64エンコード方式を試す（本番環境用）
            base64_key = os.getenv('GOOGLE_SERVICE_ACCOUNT_BASE64')
            if base64_key:
                print(f"🔍 デバッグ: Base64方式で認証情報読み込み")
                import base64
                decoded_key = base64.b64decode(base64_key).decode('utf-8')
                service_account_info = json.loads(decoded_key)

                self.credentials = service_account.Credentials.from_service_account_info(
                    service_account_info,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                self.service = build('sheets', 'v4', credentials=self.credentials)
                print(f"✅ Google Sheets API初期化成功（Base64方式）")
                return

            print("⚠️ Google Sheets API認証情報が設定されていません")
            print(f"   GOOGLE_APPLICATION_CREDENTIALS: {credentials_path}")
            print(f"   GOOGLE_SERVICE_ACCOUNT_BASE64: {'設定済み' if base64_key else '未設定'}")
            self.service = None
        except Exception as e:
            print(f"⚠️ Google Sheets API初期化エラー: {e}")
            self.service = None

    async def export_matching_debug(
        self,
        sheet_id: str,
        input_conditions: Dict[str, Any],
        step_calculations: List[Dict[str, Any]],
        final_results: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        16列完全版マッチングデータをGoogle Sheetsにエクスポート
        毎回新しいシートを作成して履歴を保持
        """
        if self.service is None:
            raise Exception("Google Sheets API サービスが初期化されていません")

        try:
            # タイムスタンプ付きの新しいシート名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sheet_name = f"診断結果_{timestamp}"

            # セッションIDがある場合は追加
            session_id = input_conditions.get("session_id", "")
            if session_id:
                session_short = session_id[:8]  # 最初の8文字のみ使用
                sheet_name = f"診断結果_{timestamp}_{session_short}"

            # 新しいワークシートを作成
            await self._create_new_worksheet(sheet_id, sheet_name)

            # ヘッダー行を作成（16列）
            header = [
                "タレント名", "カテゴリー", "VR人気度", "TPRスコア", "従来スコア",
                "おもしろさ", "清潔感", "個性的な", "信頼できる", "かわいい",
                "カッコいい", "大人の魅力", "従来順位", "業種別イメージ",
                "最終スコア", "最終順位"
            ]

            # データ行を作成
            data_rows = []
            for result in final_results:
                row = [
                    result.get("タレント名", ""),
                    result.get("カテゴリー", ""),
                    result.get("VR人気度", 0),
                    result.get("TPRスコア", 0),
                    result.get("従来スコア", 0),
                    result.get("おもしろさ", 0),
                    result.get("清潔感", 0),
                    result.get("個性的な", 0),
                    result.get("信頼できる", 0),
                    result.get("かわいい", 0),
                    result.get("カッコいい", 0),
                    result.get("大人の魅力", 0),
                    result.get("従来順位", 0),
                    result.get("業種別イメージ", 0),
                    result.get("最終スコア", 0),
                    result.get("最終順位", 0)
                ]
                data_rows.append(row)

            # 全データを準備
            all_data = [header] + data_rows

            # メタデータを追加（別のシートまたは下部に）
            # 16列に合わせて空セルを追加
            empty_cols = [""] * 15  # 残り15列を空にする
            metadata = [
                [""] * 16,  # 空行
                ["実行条件"] + empty_cols,
                [f"業種: {input_conditions.get('industry', '')}"] + empty_cols,
                [f"ターゲット層: {', '.join(input_conditions.get('target_segments', []))}"] + empty_cols,
                [f"目的: {input_conditions.get('purpose', '')}"] + empty_cols,
                [f"予算: {input_conditions.get('budget', '')}"] + empty_cols,
                [f"実行日時: {input_conditions.get('timestamp', '')}"] + empty_cols,
                [""] * 16,  # 空行
                ["分析詳細"] + empty_cols,
                [f"分析対象タレント数: {len(final_results)}"] + empty_cols,
                [f"マッチングロジック: 5段階処理"] + empty_cols,
                [f"データ形式: 16列完全版"] + empty_cols
            ]

            # メタデータを追加
            for meta_row in metadata:
                all_data.append(meta_row)

            # 新しいシートにデータを書き込み
            range_name = f"{sheet_name}!A1:P{len(all_data)}"
            body = {
                'values': all_data
            }

            result = self.service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

            # 新しいシートのsheetIdを取得してフォーマット適用
            await self._apply_sheet_formatting(sheet_id, sheet_name, len(final_results))

            return {
                "status": "success",
                "message": f"新しいシート「{sheet_name}」に16列完全版データをエクスポートしました（{len(final_results)}件）",
                "sheet_url": f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit",
                "sheet_name": sheet_name,
                "exported_rows": len(data_rows),
                "columns": 16,
                "timestamp": timestamp
            }

        except Exception as e:
            raise Exception(f"Google Sheets エクスポートエラー: {str(e)}")
        """
        マッチングロジックの詳細データをGoogle Sheetsにエクスポート

        Args:
            sheet_id: Google Sheets ID
            input_conditions: 診断入力条件
            step_calculations: ステップ別計算過程
            final_results: 最終結果データ

        Returns:
            エクスポート結果情報
        """
        if not self.service:
            return {
                "status": "error",
                "message": "Google Sheets APIが利用できません"
            }

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # シート名を動的生成
            sheet_name = f"診断結果_{timestamp.replace(':', '-').replace(' ', '_')}"

            # 新しいワークシートを作成
            await self._create_worksheet(sheet_id, sheet_name)

            # データを構造化してシートに書き込み
            await self._write_input_conditions(sheet_id, sheet_name, input_conditions, timestamp)
            await self._write_step_calculations(sheet_id, sheet_name, step_calculations)
            await self._write_final_results(sheet_id, sheet_name, final_results)

            sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=0"

            return {
                "status": "success",
                "message": f"データエクスポート完了: {sheet_name}",
                "sheet_url": sheet_url,
                "timestamp": timestamp
            }

        except HttpError as e:
            return {
                "status": "error",
                "message": f"Google Sheets API エラー: {e}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"予期しないエラー: {e}"
            }

    async def _create_new_worksheet(self, sheet_id: str, sheet_name: str):
        """新しいワークシート作成（履歴保存用）"""
        request_body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': sheet_name,
                        'gridProperties': {
                            'rowCount': 100,
                            'columnCount': 20
                        },
                        'tabColor': {
                            'red': 0.8,
                            'green': 0.9,
                            'blue': 1.0
                        }
                    }
                }
            }]
        }

        self.service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body=request_body
        ).execute()

    async def _apply_sheet_formatting(self, sheet_id: str, sheet_name: str, data_count: int):
        """新しいシートの書式設定を適用"""
        try:
            # スプレッドシート情報を取得して新しいシートのIDを見つける
            spreadsheet = self.service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            target_sheet_id = None

            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    target_sheet_id = sheet['properties']['sheetId']
                    break

            if target_sheet_id is None:
                print(f"シート '{sheet_name}' が見つかりません")
                return

            # ヘッダー行の書式設定
            format_requests = [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": target_sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": 16
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 1.0},
                                "textFormat": {"bold": True}
                            }
                        },
                        "fields": "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat.bold"
                    }
                }
            ]

            # フォーマットを適用
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={"requests": format_requests}
            ).execute()

        except Exception as e:
            print(f"書式設定エラー: {e}")

    async def _create_worksheet(self, sheet_id: str, sheet_name: str):
        """新しいワークシートを作成"""
        request_body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': sheet_name,
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 26
                        }
                    }
                }
            }]
        }

        self.service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body=request_body
        ).execute()

    async def _write_input_conditions(
        self,
        sheet_id: str,
        sheet_name: str,
        conditions: Dict[str, Any],
        timestamp: str
    ):
        """入力条件をシートに書き込み"""
        headers = [
            "エクスポート日時", "業種", "ターゲット層", "起用目的", "予算", "診断結果URL"
        ]

        values = [
            timestamp,
            conditions.get('industry', ''),
            ', '.join(conditions.get('target_segments', [])),
            conditions.get('purpose', ''),
            conditions.get('budget', ''),
            conditions.get('result_url', '')
        ]

        range_name = f"{sheet_name}!A1:F2"
        body = {
            'values': [headers, values]
        }

        self.service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

    async def _write_step_calculations(
        self,
        sheet_id: str,
        sheet_name: str,
        calculations: List[Dict[str, Any]]
    ):
        """ステップ別計算過程をシートに書き込み"""
        start_row = 4
        headers = ["ステップ", "説明", "候補数", "フィルタ後", "備考"]

        values = [headers]
        for calc in calculations:
            values.append([
                f"Step {calc.get('step', '')}",
                calc.get('description', ''),
                calc.get('candidates', ''),
                calc.get('filtered_count', ''),
                calc.get('notes', '')
            ])

        range_name = f"{sheet_name}!A{start_row}:E{start_row + len(values)}"
        body = {'values': values}

        self.service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

    async def _write_final_results(
        self,
        sheet_id: str,
        sheet_name: str,
        results: List[Dict[str, Any]]
    ):
        """最終結果データをシートに書き込み"""
        start_row = 10

        # ヘッダー行（スクリーンショットの列構造に合わせる）
        headers = [
            "順位", "タレント名", "カテゴリー", "人気度", "知名度", "従来スコア",
            "おもしろい", "清潔感がある", "個性的な", "信頼できる", "かわいい", "カッコいい",
            "大人の魅力", "従来順位", "業種別イメージスコア", "最終スコア", "最終順位"
        ]

        values = [headers]

        # データ行
        for idx, result in enumerate(results, 1):
            talent = result.get('talent', {})
            scores = result.get('scores', {})

            row = [
                idx,  # 順位
                talent.get('name', ''),
                talent.get('category', ''),
                scores.get('vr_popularity', ''),
                scores.get('vr_recognition', ''),
                scores.get('tpr_power_score', ''),
                scores.get('interesting', ''),
                scores.get('clean', ''),
                scores.get('unique', ''),
                scores.get('trustworthy', ''),
                scores.get('cute', ''),
                scores.get('cool', ''),
                scores.get('mature_appeal', ''),
                result.get('original_rank', ''),
                result.get('industry_image_score', ''),
                result.get('final_score', ''),
                result.get('matching_score', '')
            ]
            values.append(row)

        range_name = f"{sheet_name}!A{start_row}:Q{start_row + len(values)}"
        body = {'values': values}

        self.service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

        # 数式や書式設定も追加可能
        await self._apply_formatting(sheet_id, sheet_name, start_row, len(results))

    async def _apply_formatting(self, sheet_id: str, sheet_name: str, start_row: int, data_count: int):
        """シートの書式設定を適用"""
        # ヘッダー行の書式設定
        requests = [
            {
                'repeatCell': {
                    'range': {
                        'sheetId': 0,  # 実際のシートIDを取得する必要があります
                        'startRowIndex': start_row - 1,
                        'endRowIndex': start_row,
                        'startColumnIndex': 0,
                        'endColumnIndex': 17
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.8, 'green': 0.9, 'blue': 1.0},
                            'textFormat': {'bold': True}
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            }
        ]

        body = {'requests': requests}

        try:
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body=body
            ).execute()
        except Exception as e:
            print(f"書式設定エラー: {e}")

    async def export_to_sheets(
        self,
        data: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        診断結果データをGoogle Sheetsにエクスポート
        matching.pyから呼び出される統一インターフェース

        Args:
            data: タレントマッチング結果データのリスト
            metadata: 診断条件などのメタデータ

        Returns:
            エクスポート結果の辞書
        """
        if self.service is None:
            raise Exception("Google Sheets API サービスが初期化されていません")

        try:
            # Google Sheets IDを環境変数から取得
            sheet_id = os.getenv('GOOGLE_SHEETS_ID')
            if not sheet_id:
                raise Exception("GOOGLE_SHEETS_ID環境変数が設定されていません")

            # タイムスタンプ付きの新しいシート名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sheet_name = f"診断結果_{timestamp}"

            # セッションIDがある場合は追加
            session_id = metadata.get("session_id", "")
            if session_id:
                session_short = session_id[:8]
                sheet_name = f"診断結果_{timestamp}_{session_short}"

            # 新しいワークシートを作成
            await self._create_new_worksheet(sheet_id, sheet_name)

            # ヘッダー行を作成（16列）
            header = [
                "タレント名", "カテゴリー", "VR人気度", "TPRスコア", "従来スコア",
                "おもしろさ", "清潔感", "個性的な", "信頼できる", "かわいい",
                "カッコいい", "大人の魅力", "従来順位", "業種別イメージ",
                "最終スコア", "最終順位"
            ]

            # データ行を作成
            data_rows = []
            for result in data:
                row = [
                    result.get("タレント名", ""),
                    result.get("カテゴリー", ""),
                    result.get("VR人気度", 0),
                    result.get("TPRスコア", 0),
                    result.get("従来スコア", 0),
                    result.get("おもしろさ", 0),
                    result.get("清潔感", 0),
                    result.get("個性的な", 0),
                    result.get("信頼できる", 0),
                    result.get("かわいい", 0),
                    result.get("カッコいい", 0),
                    result.get("大人の魅力", 0),
                    result.get("従来順位", 0),
                    result.get("業種別イメージ", 0),
                    result.get("最終スコア", 0),
                    result.get("最終順位", 0)
                ]
                data_rows.append(row)

            # 全データを準備
            all_data = [header] + data_rows

            # メタデータを追加
            empty_cols = [""] * 15
            metadata_rows = [
                [""] * 16,  # 空行
                ["実行条件"] + empty_cols,
                [f"実施日時: {metadata.get('実施日時', '')}"] + empty_cols,
                [f"業種: {metadata.get('業種', '')}"] + empty_cols,
                [f"ターゲット: {metadata.get('ターゲット', '')}"] + empty_cols,
                [f"予算: {metadata.get('予算', '')}"] + empty_cols,
                [f"起用目的: {metadata.get('起用目的', '')}"] + empty_cols,
                [f"企業名: {metadata.get('企業名', '')}"] + empty_cols,
                [f"担当者: {metadata.get('担当者', '')}"] + empty_cols,
                [""] * 16,  # 空行
                ["分析詳細"] + empty_cols,
                [f"分析対象タレント数: {len(data)}"] + empty_cols,
                [f"マッチングロジック: 5段階処理"] + empty_cols,
                [f"データ形式: 16列完全版"] + empty_cols
            ]

            for meta_row in metadata_rows:
                all_data.append(meta_row)

            # 新しいシートにデータを書き込み
            range_name = f"{sheet_name}!A1:P{len(all_data)}"
            body = {'values': all_data}

            result = self.service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

            # シートの書式設定を適用
            await self._apply_sheet_formatting(sheet_id, sheet_name, len(data))

            return {
                "status": "success",
                "message": f"新しいシート「{sheet_name}」にデータをエクスポートしました（{len(data)}件）",
                "sheet_url": f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit",
                "sheet_name": sheet_name,
                "exported_rows": len(data_rows),
                "columns": 16,
                "timestamp": timestamp
            }

        except Exception as e:
            raise Exception(f"Google Sheets エクスポートエラー: {str(e)}")