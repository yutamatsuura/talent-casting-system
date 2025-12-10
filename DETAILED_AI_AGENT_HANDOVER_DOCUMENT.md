# AI エージェント詳細引き継ぎドキュメント

## 📋 プロジェクト概要

### プロジェクト構成
```
talent-casting-form/
├── frontend/          # Next.js 診断システム (localhost:3248)
├── landing/          # 静的LP (Vercel e-spirit プロジェクト)
├── backend/          # FastAPI サーバー (localhost:8432)
└── docs/            # プロジェクト文書
```

### 運用中のサービス
- **フロントエンド**: `http://localhost:3248` (診断システム)
- **バックエンド**: `http://localhost:8432` (FastAPI)
- **本番LP**: `https://e-spirit.vercel.app` (Vercel)
- **データベース**: PostgreSQL (Neon Launch $19/月)

---

## 🎯 実行した作業の詳細

### 1. FV (First View) 要素統合作業

#### 問題の背景
- クライアントが新しいAIAgentデザインのFV要素を提供
- 既存のLP診断ボタン機能を壊さずに統合する必要

#### 実施内容
**ソースファイル**: `/Users/lennon/Downloads/sass-base-aitalent 3/index.html`
**ターゲット**: `/Users/lennon/projects/talent-casting-form/landing/index.html`

**重要な発見**: ソースファイルの診断ボタンが `href=""` で空だった
```html
<!-- ❌ ソースファイル（機能しない） -->
<a href="" class="f-s">無料で診断する</a>

<!-- ✅ 統合後（機能保持） -->
<a href="http://localhost:3248/diagnosis" class="f-s">無料で診断する</a>
```

**統合されたFVセクションの完全コード**:
```html
<section class="fv" id="fv">
  <div class="fv-main container flex">
    <div class="fv-main-left">
      <h1 class="c-blue f-xl f-700">
        貴社に最適な<br>
        タレント<span class="c-green">診断</span>
      </h1>
      <p class="f-m">
        25年間の蓄積データ×AIの独自アルゴリズムで<br>
        貴社に最適なタレントを提案します。<br>
        <strong>タレントリスト提供サービスあり。</strong>
      </p>
      <div class="fv-main-shindan">
        <div class="fv-main-shindan-box flex">
          <div class="fv-main-shindan-box-left">
            <img src="img/img-shindan.png" alt="">
          </div>
          <div class="fv-main-shindan-box-right">
            <span class="c-blue f-s f-700">e-Spirit</span>
            <strong class="d-block f-m f-700">AIエージェント</strong>
            <p class="f-xs">25年間の蓄積データ×AIの独自アルゴリズムで貴社に最適なタレントを提案します。<br>タレントリスト提供サービスあり。</p>
            <div class="btn">
              <a href="http://localhost:3248/diagnosis" class="f-s">無料で診断する</a>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="fv-main-right">
      <img src="img/bg-agent.png" alt="" class="bg-agent">
    </div>
  </div>
</section>
```

#### デプロイエラーと解決
**エラー1**: 間違ったVercelプロジェクトにデプロイ
```bash
# ❌ 間違い
vercel --prod  # 「landing」という新規プロジェクトを作成

# ✅ 正解
vercel link    # 既存の「e-spirit」プロジェクトにリンク
vercel --prod  # 正しいプロジェクトにデプロイ
```

**エラー2**: 空のページが表示
- 原因: `/frontend/landing/` ディレクトリからデプロイ（空のindex.html）
- 解決: `/landing/` ディレクトリに変更

**最終デプロイ結果**:
- URL: `https://e-spirit.vercel.app`
- ファイル数: 43ファイル
- 状態: 正常動作確認済み

### 2. 診断フォームバグ修正

#### 問題
質問3/6「起用目的」でページに入ると「その他」が初期選択された状態になる

#### 原因特定
`/Users/lennon/projects/talent-casting-form/frontend/src/components/diagnosis/FormSteps/FormStep3.tsx`
58行目の条件分岐エラー:

```typescript
// ❌ 問題のあるコード
value={isPresetReason ? formData.q3_2 : 'その他'}

// 論理的に間違い:
// - isPresetReason が false の時に 'その他' が固定で設定される
// - ユーザーが何も選択していない状態でも 'その他' が表示される
```

#### 修正内容
```typescript
// ✅ 修正後のコード
value={formData.q3_2 || ''}

// 正しい動作:
// - formData.q3_2 に値がある場合はその値を表示
// - 値がない場合は空文字（何も選択されていない状態）
```

#### 検証結果
- 初期状態: 何も選択されていない
- ユーザー選択後: 選択した値が正しく保持される
- フォーム送信: バリデーションも正常動作

### 3. Google Sheets API基盤実装

#### 要件分析
クライアントからの要求:
- マッチングロジックの各ステップ詳細をGoogleシートにエクスポート
- フロントエンド表示は不要（バックエンドのみ）
- テスト・検証用途

#### 技術選択理由
1. **Google Sheets API**: エクセルより共有・リアルタイム編集が容易
2. **サービスアカウント認証**: ユーザー認証不要で自動化可能
3. **FastAPI統合**: 既存APIエンドポイントとして提供

#### 実装アーキテクチャ
```
診断リクエスト → マッチングロジック実行 → デバッグデータ収集 → Google Sheets書き込み
      ↓                 ↓                  ↓              ↓
  [API呼び出し]    [matching_logic.py]  [debug収集]    [sheets_exporter]
```

#### 詳細実装

##### 1. Google Cloud設定
**プロジェクト**: `talent-casting-1764281842`

**サービスアカウント作成手順**:
1. Google Cloud Console → IAM → サービスアカウント
2. アカウント名: `app-service-account`
3. 権限: Editor（今後最小権限に変更推奨）
4. JSONキー生成: `/Users/lennon/Downloads/talent-casting-1764281842-5c90eabcf00d.json`

**環境変数設定**:
```bash
# /Users/lennon/projects/talent-casting-form/backend/.env
GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", "project_id": "talent-casting-1764281842", ...}'
```

##### 2. SheetsExporter サービス実装
**ファイル**: `/Users/lennon/projects/talent-casting-form/backend/app/services/sheets_exporter.py`

**主要機能**:
```python
class SheetsExporter:
    def __init__(self):
        """Google Sheets API認証とサービス初期化"""

    async def export_matching_debug(self, sheet_id, input_conditions, step_calculations, final_results):
        """メイン機能: マッチングデバッグデータをシートに出力"""

    def _write_input_conditions(self, sheet, input_conditions):
        """入力条件シートを作成・書き込み"""

    def _write_step_calculations(self, sheet, step_calculations):
        """計算ステップシートを作成・書き込み"""

    def _write_final_results(self, sheet, final_results):
        """最終結果シートを作成・書き込み"""
```

**出力データ構造**:

*Sheet 1: 入力条件*
```
| 項目 | 値 |
|------|-----|
| 業種 | 化粧品・ヘアケア・オーラルケア |
| ターゲット層 | 女性20-34歳 |
| 起用目的 | 認知度向上 |
| 予算 | 1000万円～3000万円未満 |
| 実行日時 | 2025-12-08 16:30:15 |
| 結果URL | /results?industry=化粧品 |
```

*Sheet 2: 計算ステップ*
```
| ステップ | 説明 | 対象数 | 詳細 |
|----------|------|--------|------|
| Step 0 | 予算フィルタリング | 1234件 | 予算範囲でフィルタ |
| Step 1 | 基礎パワー得点 | 1234件 | VR+TPR平均値 |
| Step 2 | 業種イメージ査定 | 1234件 | パーセンタイル加減点 |
| Step 3 | 基礎反映得点 | 1234件 | Step1+Step2合算 |
| Step 4 | ランキング確定 | 30件 | 上位30名抽出 |
| Step 5 | スコア振り分け | 30件 | 86-99.7点ランダム |
```

*Sheet 3: 最終結果*
```
| 順位 | タレント名 | カテゴリ | 最終スコア | 人気度 | 知名度 | おもしろい | 清潔感 | ... |
|------|------------|----------|------------|--------|--------|------------|--------|-----|
| 1 | ○○○○ | アーティスト | 99.7 | 85 | 92 | 78 | 88 | ... |
| 2 | △△△△ | 俳優 | 98.5 | 91 | 88 | 65 | 92 | ... |
```

##### 3. MatchingLogicDebug サービス
**ファイル**: `/Users/lennon/projects/talent-casting-form/backend/app/services/matching_logic_debug.py`

**目的**: 既存のマッチングロジックを再利用し、詳細な計算過程を記録

```python
class MatchingLogicDebug:
    async def execute_matching_with_debug(self, industry, target_segments, purpose, budget):
        """
        既存マッチングロジック + デバッグ情報収集

        Returns:
            Tuple[最終結果, デバッグ情報]
        """
        # 1. 既存のマッチングロジック実行
        talent_results = await execute_5_step_matching_logic(
            industry=industry,
            target_segment=target_segments[0],
            budget=budget
        )

        # 2. おすすめタレント取得
        recommended_talent_ids = await get_recommended_talents_for_matching(
            industry, target_segments[0]
        )

        # 3. CM競合チェック
        cm_status_map = await check_cm_exclusion_status(account_ids, industry)

        # 4. デバッグ情報構築
        debug_data = {
            "input_conditions": {...},
            "step_calculations": [...],
            "final_results": [...],
            "summary": {...}
        }

        return final_results, debug_data
```

##### 4. Admin Debug API
**ファイル**: `/Users/lennon/projects/talent-casting-form/backend/app/api/endpoints/admin_debug.py`

**メインエンドポイント**:
```python
@router.post("/export-matching-debug")
async def export_matching_debug(request: SheetsExportRequest):
    """
    マッチングロジック実行 + Google Sheetsエクスポート
    """
    # 1. マッチング実行
    matching_logic = MatchingLogicDebug()
    final_results, debug_data = await matching_logic.execute_matching_with_debug(...)

    # 2. Google Sheetsエクスポート
    sheets_exporter = SheetsExporter()
    export_result = await sheets_exporter.export_matching_debug(...)

    return MatchingDebugResponse(...)
```

**リクエスト例**:
```json
{
  "sheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "industry": "化粧品・ヘアケア・オーラルケア",
  "target_segments": "女性20-34歳",
  "purpose": "認知度向上",
  "budget": "1000万円～3000万円未満",
  "export_immediately": true
}
```

**補助エンドポイント**:
1. `GET /api/admin/test-sheets-connection`: Google Sheets接続テスト
2. `POST /api/admin/matching-test`: エクスポートなしでマッチング実行のみ

#### 発生したエラーと解決過程

##### エラー1: ImportError - MatchingRequest不明
```
ImportError: cannot import name 'MatchingRequest' from 'app.schemas.matching'
```

**原因**: `admin_debug.py` で存在しないクラスをimport
**修正**: 正しいクラス名 `MatchingFormData` に変更
```python
# ❌ 修正前
from app.schemas.matching import MatchingRequest

# ✅ 修正後
from app.schemas.matching import MatchingFormData
```

##### エラー2: ModuleNotFoundError - app.services.database
```
ModuleNotFoundError: No module named 'app.services.database'
```

**原因**: `matching_logic_debug.py` で存在しないモジュールをimport
**修正**: 不要なimportを削除
```python
# ❌ 削除
from app.services.database import get_database_connection

# ✅ 既存のmatching.pyから必要な関数のみimport
from app.api.endpoints.matching import execute_5_step_matching_logic, check_cm_exclusion_status, get_recommended_talents_for_matching
```

##### エラー3: ModuleNotFoundError - google libraries
```
ModuleNotFoundError: No module named 'google'
```

**修正**: 必要なライブラリをインストール
```bash
cd backend
source venv/bin/activate
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

##### エラー4: サーバー起動阻害
**対処**: 一時的にadmin_debug router を無効化
```python
# backend/app/main.py 86行目
# app.include_router(admin_debug.router, tags=["Debug Export"])
```

これによりサーバーは正常起動。Google Sheets設定完了後に有効化予定。

---

## 🚧 未完了事項の詳細

### 1. Google Cloud Console API有効化

#### 手順
1. https://console.cloud.google.com/apis/library にアクセス
2. 右上でプロジェクト `talent-casting-1764281842` を選択
3. 検索ボックスに「Google Sheets API」と入力
4. Google Sheets API をクリック
5. 「有効にする」ボタンをクリック

#### 確認方法
```bash
# APIが有効化されているかテスト
curl -X GET "http://localhost:8432/api/admin/test-sheets-connection"
```

### 2. テスト用Googleシート作成

#### シート作成手順
1. https://sheets.google.com にアクセス
2. 「空白のスプレッドシート」を作成
3. シート名を「マッチングロジックテスト」に変更
4. URLから Sheet ID を抽出

#### Sheet ID取得方法
URLパターン: `https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit#gid=0`

例:
- URL: `https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0`
- Sheet ID: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

### 3. シート共有設定

#### 手順
1. 作成したGoogleシートを開く
2. 右上「共有」ボタンをクリック
3. 「ユーザーやグループを追加」欄に以下を入力:
   ```
   app-service-account@talent-casting-1764281842.iam.gserviceaccount.com
   ```
4. 権限を「編集者」に設定
5. 「送信」をクリック

#### 重要注意
- 通知メール送信は不要（サービスアカウントのため）
- 権限は「編集者」が必須（書き込み権限必要）

### 4. admin_debug エンドポイント有効化

#### 手順
```python
# backend/app/main.py 86行目のコメントアウトを解除
app.include_router(admin_debug.router, tags=["Debug Export"])
```

#### サーバー再起動
```bash
# バックグラウンドで動作中のサーバーは自動リロード対応済み
# ファイル保存時に自動的に変更が反映される
```

### 5. 最終動作テスト

#### テスト1: 接続確認
```bash
curl -X GET "http://localhost:8432/api/admin/test-sheets-connection"

# 期待レスポンス:
{
  "status": "success",
  "message": "Google Sheets API接続正常",
  "auth_configured": true,
  "service_available": true
}
```

#### テスト2: マッチングロジックのみ
```bash
curl -X POST "http://localhost:8432/api/admin/matching-test" \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "化粧品・ヘアケア・オーラルケア",
    "target_segments": "女性20-34歳",
    "purpose": "認知度向上",
    "budget": "1000万円～3000万円未満"
  }'
```

#### テスト3: 完全エクスポート
```bash
curl -X POST "http://localhost:8432/api/admin/export-matching-debug" \
  -H "Content-Type: application/json" \
  -d '{
    "sheet_id": "[取得したSHEET_ID]",
    "industry": "化粧品・ヘアケア・オーラルケア",
    "target_segments": "女性20-34歳",
    "purpose": "認知度向上",
    "budget": "1000万円～3000万円未満",
    "export_immediately": true
  }'

# 成功時: GoogleシートにデータがエクスポートされることをWeb UIで確認
```

---

## 🔧 技術的詳細情報

### マッチングロジックフロー
```
Step 0: 予算フィルタリング
  ↓ SQL: SELECT * FROM talents WHERE money_max_one_year <= [予算上限]

Step 1: 基礎パワー得点計算
  ↓ 計算式: (vr_popularity + tpr_power_score) / 2
  ↓ JOIN: talent_scores ON target_segment_id = [ユーザー選択]

Step 2: 業種イメージ査定 (最重要ステップ)
  ↓ PostgreSQL PERCENT_RANK() でパーセンタイル計算
  ↓ 加減点ルール: 上位15% +12点, 16-30% +6点, 31-50% +3点, 51-85% 0点, 下位15% -6点
  ↓ JOIN: talent_images × industries × image_items

Step 3: 基礎反映得点
  ↓ 計算式: Step1得点 + Step2加減点

Step 4: ランキング確定
  ↓ ORDER BY: 基礎反映得点 DESC, base_power_score DESC, talent_id
  ↓ LIMIT 30

Step 5: マッチングスコア振り分け
  ↓ ランキング別スコア範囲:
     1-3位: 97.0-99.7点
     4-10位: 93.0-96.9点
     11-20位: 89.0-92.9点
     21-30位: 86.0-88.9点
  ↓ 各範囲内でランダムに振り分け
```

### データベーススキーマ関連テーブル
```sql
-- 主要テーブル
talents                 -- タレント基本情報
talent_scores          -- VR/TPRスコア (target_segment別)
talent_images          -- タレントイメージデータ
industries             -- 業種マスタ
target_segments        -- ターゲット層マスタ
industry_images        -- 業種別イメージ項目
recommended_talents    -- おすすめタレント
m_talent_cm           -- CM出演履歴
```

### 重要なPython依存関係
```txt
# backend/requirements.txt (Google Sheets関連追加分)
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
google-api-python-client==2.108.0
```

### 環境変数構成
```bash
# backend/.env
DATABASE_URL=postgresql://[username]:[password]@[host]/[database]
CORS_ORIGIN=http://localhost:3248
NODE_ENV=development
GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'
```

---

## 🔍 トラブルシューティング

### よくあるエラーパターン

#### 1. Google Sheets API認証エラー
```
google.auth.exceptions.DefaultCredentialsError: Could not automatically determine credentials
```

**原因**: 環境変数が正しく設定されていない
**確認方法**:
```bash
echo $GOOGLE_SERVICE_ACCOUNT_JSON | head -c 100
# {"type": "service_account", "project_id": "talent-casting-1764281842", ... が表示されるべき
```

#### 2. Sheet ID不正エラー
```
googleapiclient.errors.HttpError: <HttpError 404 when requesting ... returned "Requested entity was not found.">
```

**原因**:
- Sheet IDが間違っている
- サービスアカウントに共有権限がない

**確認方法**:
1. Sheet URLを再確認
2. 共有設定でサービスアカウントが表示されるかチェック

#### 3. 権限不足エラー
```
googleapiclient.errors.HttpError: <HttpError 403 when requesting ... returned "The caller does not have permission">
```

**原因**: サービスアカウントの権限が「閲覧者」になっている
**修正**: シートの共有設定で「編集者」に変更

#### 4. APIクォータ超過
```
googleapiclient.errors.HttpError: <HttpError 429 when requesting ... returned "Quota exceeded">
```

**対処**:
- 1日あたりの上限: 100リクエスト/100秒
- 大量テスト時は間隔を空ける

### デバッグ支援機能

#### ログ出力設定
```python
# sheets_exporter.py内でデバッグログ有効化
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 段階的テスト手順
1. `GET /api/admin/test-sheets-connection` でAPI接続確認
2. `POST /api/admin/matching-test` でマッチングロジックのみテスト
3. `POST /api/admin/export-matching-debug` で完全統合テスト

---

## 📞 引き継ぎチェックリスト

### 環境確認
- [ ] サーバー `localhost:8432` が稼働中
- [ ] フロントエンド `localhost:3248` が稼働中
- [ ] `.env` ファイルにGoogle認証情報が設定済み
- [ ] `backend/venv` が有効化された状態

### 設定作業
- [ ] Google Cloud Console でSheets API有効化
- [ ] テスト用Googleシート作成
- [ ] シート共有設定 (サービスアカウントに編集権限)
- [ ] admin_debug router のコメントアウト解除
- [ ] 3段階テスト実行と動作確認

### ファイル状態
- [ ] `backend/app/main.py` 86行目の修正待ち
- [ ] Google Sheets関連ライブラリインストール済み
- [ ] 全importエラー解決済み

### 最終確認項目
- [ ] マッチングロジックの実行結果がGoogleシートに正しく出力される
- [ ] 入力条件・計算ステップ・最終結果の3シートが作成される
- [ ] タレントデータ（ランキング・スコア・VR/TPR値）が正確に反映される

---

**最終更新**: 2025-12-08 17:00
**詳細度**: 完全版（全技術詳細・エラー履歴・手順書含む）
**引き継ぎ先**: 次期AI Agent（Google Sheets設定完了作業担当）

---

## 📎 参考リンク・資料

### Google Cloud関連
- [Google Sheets API v4 Documentation](https://developers.google.com/sheets/api/guides/concepts)
- [Service Account Authentication](https://cloud.google.com/docs/authentication/getting-started)
- [API Usage Limits](https://developers.google.com/sheets/api/limits)

### プロジェクト内文書
- `CLAUDE.md`: プロジェクト基本設定
- `docs/SCOPE_PROGRESS.md`: 開発進捗管理
- `backend/README.md`: バックエンド技術仕様

### 動作中のバックグラウンドプロセス
```bash
# 確認コマンド
ps aux | grep -E "(uvicorn|npm|vercel)"

# 主要プロセス:
# - uvicorn app.main:app (FastAPI server)
# - npm run dev (Next.js frontend)
# - vercel --prod (Vercel deployments)
# - gcloud builds submit (Cloud Run deployments)
```