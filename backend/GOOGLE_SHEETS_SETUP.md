# Google Sheets エクスポート機能セットアップ手順

## 概要
マッチングロジックの詳細データをGoogle Sheetsにエクスポートする機能のセットアップ手順書です。

## 🎯 完成後の機能

### 利用可能なAPIエンドポイント
- `POST /api/admin/export-matching-debug` - 詳細データエクスポート
- `POST /api/admin/matching-test` - マッチングロジックテスト（エクスポートなし）
- `GET /api/admin/test-sheets-connection` - Google Sheets接続テスト

### エクスポートされるデータ
- **入力条件シート**: 業種、ターゲット層、起用目的、予算
- **ステップ計算シート**: Step0-5の各段階の詳細計算過程
- **最終結果シート**: スクリーンショット形式のタレントランキング詳細

---

## 📋 必要な事前準備

### 1. Google Cloud Console設定

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成またはプロジェクトを選択
3. Google Sheets APIを有効化:
   - 「APIとサービス」→「ライブラリ」
   - 「Google Sheets API」を検索して有効化

### 2. サービスアカウント作成

1. 「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「サービスアカウント」
3. サービスアカウント名: `talent-casting-sheets-exporter`
4. 役割: `Project > Editor`（最小権限に後で変更推奨）
5. JSONキーファイルをダウンロード

### 3. テスト用スプレッドシート作成

1. [Google Sheets](https://sheets.google.com/)で新しいスプレッドシートを作成
2. スプレッドシート名: `タレントキャスティング_マッチングテスト`
3. URLからスプレッドシートIDを取得:
   ```
   https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit
   ```
4. サービスアカウントメールアドレスを編集者として共有追加

---

## ⚙️ 環境変数設定

### ローカル開発環境
```bash
# backend/.env に追加
GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account","project_id":"your-project","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...","client_email":"talent-casting-sheets-exporter@your-project.iam.gserviceaccount.com","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/talent-casting-sheets-exporter%40your-project.iam.gserviceaccount.com"}'
```

### 本番環境 (Google Cloud Run)
環境変数として設定:
```bash
gcloud run services update talent-casting-api \
  --set-env-vars GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
```

---

## 🧪 動作確認手順

### 1. 接続テスト
```bash
curl -X GET "http://localhost:8432/api/admin/test-sheets-connection"
```

**期待する応答:**
```json
{
  "status": "success",
  "message": "Google Sheets API接続正常",
  "auth_configured": true,
  "service_available": true
}
```

### 2. マッチングロジックテスト（エクスポートなし）
```bash
curl -X POST "http://localhost:8432/api/admin/matching-test" \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "化粧品・ヘアケア・オーラルケア",
    "target_segments": ["女性20-34"],
    "purpose": "認知度向上",
    "budget": "1000万円～3000万円未満"
  }'
```

### 3. Google Sheetsエクスポート実行
```bash
curl -X POST "http://localhost:8432/api/admin/export-matching-debug" \
  -H "Content-Type: application/json" \
  -d '{
    "sheet_id": "YOUR_SPREADSHEET_ID",
    "industry": "化粧品・ヘアケア・オーラルケア",
    "target_segments": ["女性20-34"],
    "purpose": "認知度向上",
    "budget": "1000万円～3000万円未満",
    "export_immediately": true
  }'
```

**期待する応答:**
```json
{
  "status": "success",
  "message": "マッチングロジック実行完了",
  "export_result": {
    "status": "success",
    "message": "データエクスポート完了: 診断結果_2025-12-08_15-30-00",
    "sheet_url": "https://docs.google.com/spreadsheets/d/YOUR_ID/edit#gid=0",
    "timestamp": "2025-12-08 15:30:00"
  },
  "sheet_url": "https://docs.google.com/spreadsheets/d/YOUR_ID/edit#gid=0"
}
```

---

## 📊 エクスポート結果の確認

### Google Sheetsに作成されるタブ
1. **診断結果_[タイムスタンプ]**: メインデータシート
   - A1-F2: 入力条件（日時、業種、ターゲット層、目的、予算、URL）
   - A4-E9: ステップ計算過程（Step0-5の詳細）
   - A10-Q40: 最終結果（スクリーンショット準拠の列構造）

### データ列構造
```
順位 | タレント名 | カテゴリー | 人気度 | 知名度 | 従来スコア |
おもしろい | 清潔感がある | 個性的な | 信頼できる | かわいい | カッコいい |
大人の魅力 | 従来順位 | 業種別イメージスコア | 最終スコア | 最終順位
```

---

## 🔧 トラブルシューティング

### よくあるエラー

1. **認証エラー**:
   ```
   "Google Sheets APIサービスが初期化されていません"
   ```
   → 環境変数 `GOOGLE_SERVICE_ACCOUNT_JSON` が正しく設定されているか確認

2. **権限エラー**:
   ```
   "The caller does not have permission"
   ```
   → スプレッドシートにサービスアカウントが編集者として追加されているか確認

3. **スプレッドシートIDエラー**:
   ```
   "Requested entity was not found"
   ```
   → スプレッドシートIDが正しいか、公開設定を確認

### デバッグログ確認
```bash
# バックエンドのログを確認
tail -f logs/fastapi.log | grep "Sheets"
```

---

## 💼 使用例・活用方法

### 開発・テスト段階での活用
1. **マッチングロジック検証**: 各ステップの計算が正しいか数式レベルで確認
2. **A/Bテスト**: 異なる条件での結果比較
3. **データ品質チェック**: タレントデータの欠損・異常値検出

### 本番運用での活用
1. **顧客向けレポート**: 診断結果の詳細データをクライアントに提供
2. **ビジネス分析**: 診断傾向・人気タレントの分析材料
3. **システム監視**: 異常な結果パターンの早期発見

---

## ⚠️ セキュリティ・運用注意点

1. **サービスアカウントキー管理**:
   - JSONキーファイルは厳重に管理
   - 定期的なキーローテーション推奨

2. **アクセス制限**:
   - 管理者エンドポイントには適切な認証を実装（将来）
   - IPアドレス制限やVPN経由アクセスを検討

3. **データプライバシー**:
   - 個人情報を含むデータの取り扱いに注意
   - エクスポート先シートのアクセス権限管理

4. **API利用制限**:
   - Google Sheets API は1日あたり100リクエスト/分の制限あり
   - 大量エクスポート時は間隔調整が必要