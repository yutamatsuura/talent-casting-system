# プロジェクト設定

## 基本設定
```yaml
プロジェクト名: タレントキャスティングシステム
開始日: 2025-11-28
技術スタック:
  frontend:
    lp: HTML/CSS + Vercel
    diagnosis: Next.js 15 + TypeScript 5 + Vercel
  backend: FastAPI + Python 3.11+
  database: PostgreSQL 16 (Neon Launch $19/月)
  hosting:
    lp: yourdomain.com (Vercel静的)
    diagnosis: app.yourdomain.com (Vercel)
    api: Google Cloud Run
```

## アーキテクチャ構成
```yaml
サブドメイン分離:
  メインLP: yourdomain.com (HTML/CSS)
  診断システム: app.yourdomain.com (Next.js)
  API: FastAPI (Google Cloud Run)

開発方針:
  - LP制作チームと診断システム開発の独立作業
  - 将来のLP差し替え対応（暫定版 → 本格版）
  - Vercel無料プラン × 2プロジェクト運用
```

## 開発環境
```yaml
ポート設定:
  # 複数プロジェクト並行開発のため、一般的でないポートを使用
  lp_dev: 3247 (開発時ローカルサーバー)
  diagnosis: 3248 (Next.js診断システム)
  api: 8432 (FastAPI)
  database: 5433 (PostgreSQL、デフォルト5432を避ける)

環境変数:
  設定ファイル: .env.local（ルートディレクトリ）
  必須項目:
    - DATABASE_URL (Neon PostgreSQL接続文字列)
    - NEXTAUTH_SECRET (セッション管理、将来用)
    - API_BASE_URL (FastAPI エンドポイント)
    - NODE_ENV (development/production)
```

## テスト認証情報
```yaml
開発用データ:
  # 認証機能なし（公開アクセス）のため最小限
  test_industry: 化粧品・ヘアケア・オーラルケア
  test_target: ["女性20-34", "女性35-49"]
  test_budget: 1,000万円～3,000万円未満
  test_company: 株式会社テストクライアント
  test_email: test@talent-casting-dev.local

外部サービス:
  Neon: Launch($19/月)、クライアント契約
  Vercel: 無料プラン × 2プロジェクト
  Google Cloud Run: 従量課金、クライアント契約
```

## コーディング規約

### 命名規則
```yaml
ファイル名:
  - LP: kebab-case.html (例: talent-casting-lp.html)
  - Next.jsコンポーネント: PascalCase.tsx (例: TalentCastingForm.tsx)
  - ユーティリティ: camelCase.ts (例: matchingLogic.ts)
  - 定数: UPPER_SNAKE_CASE.ts (例: API_ENDPOINTS.ts)
  - FastAPI: snake_case.py (例: matching_logic.py)

変数・関数:
  - 変数: camelCase (JavaScript/TypeScript), snake_case (Python)
  - 関数: camelCase (JavaScript/TypeScript), snake_case (Python)
  - 定数: UPPER_SNAKE_CASE
  - 型/インターフェース: PascalCase
```

### コード品質
```yaml
必須ルール:
  - TypeScript: strictモード有効
  - Python: type hints必須、mypy準拠
  - 未使用の変数/import禁止
  - console.log本番環境禁止
  - エラーハンドリング必須
  - 関数行数: 100行以下（96.7%カバー）
  - ファイル行数: 700行以下（96.9%カバー）
  - 複雑度: 10以下
  - 行長: 120文字

フォーマット:
  - インデント: スペース2つ (JS/TS), スペース4つ (Python)
  - セミコロン: あり (JS/TS)
  - クォート: シングル (JS/TS), ダブル (Python)
```

## プロジェクト固有ルール

### APIエンドポイント
```yaml
命名規則:
  - RESTful形式を厳守
  - 複数形を使用 (/talents, /industries)
  - ケバブケース使用 (/matching-result)

主要エンドポイント:
  - POST /api/matching (5段階マッチングロジック実行)
  - GET /api/health (ヘルスチェック)
  - GET /api/industries (業種マスタ取得)
  - GET /api/target-segments (ターゲット層マスタ取得)
```

### 型定義
```yaml
配置:
  frontend: src/types/index.ts
  backend: app/models/__init__.py

同期ルール:
  - FormData型は必ずフロント・バック両対応
  - TalentResult型は必ずAPI仕様書と一致
  - マスタデータ型は必ずDBスキーマと同期
```

### データベース接続
```yaml
開発環境:
  接続先: Neon Branchデータベース（本番データクローン）
  接続プール: 10-30接続（FastAPI設定）
  タイムアウト: 30秒

本番環境:
  接続先: Neon Mainブランch
  接続プール: 10-30接続
  監視: Neonダッシュボード + ログ
```

## 5段階マッチングロジック仕様

### 技術実装ポイント
```yaml
STEP 0: 予算フィルタリング
  - テーブル: talents.money_max_one_year
  - 条件: <= ユーザー選択予算上限

STEP 1: 基礎パワー得点
  - 計算式: (vr_popularity + tpr_power_score) / 2
  - テーブル: talent_scores
  - フィルタ: target_segment_id = ユーザー選択ターゲット層

STEP 2: 業種イメージ査定 (★最重要)
  - 処理: PostgreSQL PERCENT_RANK()でパーセンタイル算出
  - 加減点: 上位15% +12点、16-30% +6点...
  - テーブル: talent_images, industries, image_items

STEP 3: 基礎反映得点
  - 計算式: STEP1 + STEP2

STEP 4: ランキング確定
  - ソート: 基礎反映得点 DESC, base_power_score DESC, talent_id
  - 抽出: LIMIT 30

STEP 5: マッチングスコア振り分け
  - 1-3位: 97.0-99.7点ランダム
  - 4-10位: 93.0-96.9点ランダム
  - 11-20位: 89.0-92.9点ランダム
  - 21-30位: 86.0-88.9点ランダム
```

### パフォーマンス要件
```yaml
レスポンス目標: <3秒
設計値: 242ms (リアルタイム計算)
余裕度: 12倍

最適化戦略:
  - 複合インデックス活用
  - N+1問題回避（JOIN統合）
  - 非同期処理（FastAPI + asyncpg）
  - 接続プール最適化
```

## 🆕 最新技術情報（知識カットオフ対応）
```yaml
PostgreSQL制約 (2025年調査):
  - percentile_cont(): OVER句非対応（ORDERED-SET AGGREGATE）
  - PERCENT_RANK(): OVER句対応、代替利用
  - NTILE(): 均等分割で統計的に不正確、使用禁止

FastAPI最適化 (2025年調査):
  - asyncpg: psycopg2より2倍高速
  - SQLAlchemy 2.0: AI自動インデックスチューニング対応
  - async/await: CPU使用率3-5倍向上

Vercel制限 (2025年調査):
  - 無料プラン: 100GB/月、6,000分ビルド時間
  - サブドメイン: 無制限対応
  - 静的サイト + Next.js両対応

Neon特徴 (2025年調査):
  - ブランチ機能: Git感覚でDBクローン（瞬時・低コスト）
  - スケールトゥゼロ: 未使用時課金なし
  - Launch($19/月): 10GB、300 CU-hours、最大16 CU
```

## プロジェクト特記事項

### LP差し替え対応設計
```yaml
暫定LP (Phase 1-3):
  - 技術: HTML/CSS
  - 目的: 診断システム動作確認・開発並行進行
  - ファイル: lp/index.html, lp/styles.css

本格LP (Phase 11以降):
  - 技術: 未定（制作チーム判断）
  - 統合: app.yourdomain.com へのリンクのみ変更
  - 診断システム: 変更なし（独立性確保）
```

### エラーハンドリング戦略
```yaml
フォーム入力:
  - バリデーション: フロントエンド（リアルタイム）+ バックエンド（最終）
  - エラー表示: フィールド直下、非侵入的

API通信:
  - タイムアウト: 10秒
  - リトライ: 3回（指数バックオフ）
  - フォールバック: 「しばらくお待ちください」メッセージ

データベース:
  - 接続エラー: ヘルスチェック失敗として処理
  - クエリエラー: ログ出力 + 500エラー
  - データ不整合: 管理者通知
```

### セキュリティ設定
```yaml
本番環境必須:
  - HTTPS強制
  - セキュリティヘッダー (CSP, HSTS, X-Frame-Options)
  - レート制限 (10 req/sec per IP)
  - 入力サニタイゼーション

開発環境:
  - HTTP許可
  - デバッグログ有効
  - CORS設定: localhost許可
```

## 開発フロー

### 推奨開始手順
```yaml
1. Phase 2: Git/GitHub管理
   - 2プロジェクト分のリポジトリ作成
   - GitHub Actions設定（Vercel自動デプロイ）

2. Phase 3: フロントエンド基盤
   - LP用Vercelプロジェクト作成
   - 診断システム用Vercelプロジェクト作成
   - サブドメイン設定

3. Phase 4: ページ実装
   - 暫定LP作成
   - Next.js診断システム実装

4. Phase 5: バックエンド実装
   - FastAPI + 5段階マッチングロジック

5. Phase 6: データベース構築
   - PostgreSQL(Neon) + VR/TPRデータ移行
```

**重要**: このプロジェクトは「必要最小限の実装のみ」の原則に従い、「あったらいいな」機能は一切追加しない。

## デプロイ設定（本番環境）
```yaml
デプロイ日: 2025-12-06
構成: A (お試しデプロイ - 開発DBをそのまま使用)
技術選択: Vercel + Cloud Run + --set-env-vars方式

本番環境URL:
  フロントエンド: https://talent-casting-diagnosis-36gjbuhab-yutamatsuuras-projects.vercel.app
  バックエンド: https://talent-casting-backend-392592761218.asia-northeast1.run.app
  API Docs: https://talent-casting-backend-392592761218.asia-northeast1.run.app/api/docs
  Health Check: https://talent-casting-backend-392592761218.asia-northeast1.run.app/api/health

データベース: Neon PostgreSQL (開発環境と同じインスタンス)
環境変数管理: --set-env-vars (完全無料設定)
認証状態:
  - Vercel: ユーザー yutamatsuura
  - Google Cloud: プロジェクト talent-casting-1764281842, リージョン asia-northeast1

デプロイスクリプト: scripts/deploy-production.sh (.gitignore済み)
検証結果: Playwright自動テスト 4/4 Pass, API疎通確認済み
```

## 注意事項
- フロントエンドはVercelのパスワード保護を解除する必要があります
  (Vercel Dashboard → Settings → General → Password Protection → Disabled)
- 構成Aのため開発環境と本番環境で同じデータベースを使用しています
- 将来的な本番専用データベース切り替えも可能です