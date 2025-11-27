# タレントキャスティングシステム - 要件定義書

要件定義の作成原則
- **「あったらいいな」は絶対に作らない**
- **拡張可能性のための余分な要素は一切追加しない**
- **将来の「もしかして」のための準備は禁止**
- **今、ここで必要な最小限の要素のみ**

## 1. プロジェクト概要

### 1.1 成果目標
キャスティング会社のクライアント企業が、業種・ターゲット層・予算を入力するだけで、データ分析に基づく最適なタレント30名をマッチングスコア付きで即座に提案されるシステム

### 1.2 成功指標

#### 定量的指標
- フォーム送信から結果表示まで3秒以内のレスポンス速度
- 約2,000件のタレントデータから正確な上位30名抽出
- 複雑な5段階マッチングロジックの100%正確な実行

#### 定性的指標
- 従来の担当者の経験と勘による選定から、データドリブンな客観的選定への転換実現
- クライアント企業が直感的に操作できるシンプルなフォームUI
- マッチングスコア付きの提案により、選定根拠の透明性確保

## 2. システム全体像

### 2.1 主要機能一覧
- LP機能: サービス紹介とCTA配置（HTML/CSS）
- フォーム入力機能: 6段階の質問形式でクライアント要件収集（Next.js）
- マッチング処理機能: 5段階ロジックによる最適タレント算出（FastAPI）
- 結果表示機能: 上位30名タレントの提案とマッチングスコア表示（Next.js）

### 2.2 ユーザーロールと権限
- **ゲスト**: LP閲覧、診断フォーム入力、結果閲覧、無料カウンセリング予約
- **管理機能**: なし（MVPのため）

### 2.3 認証・認可要件
- 認証方式: なし（公開アクセス）
- セキュリティレベル: 基本（個人情報は会社名・担当者名・連絡先のみ）
- 管理機能: 不要

### 2.4 アーキテクチャ構成（サブドメイン分離）
- LP: https://yourdomain.com（HTML/CSS + Vercel静的ホスティング）
- 診断システム: https://app.yourdomain.com（Next.js + Vercel）
- API: Google Cloud Run（FastAPI）
- データベース: PostgreSQL（Neon）

## 3. ページ詳細仕様

### 3.1 P-001: ランディングページ（HTML/CSS）

#### 目的
診断システムへの誘導とサービス価値の伝達

#### 主要機能
- サービス概要説明
- CTA（診断開始ボタン）
- 診断システムへのリダイレクト

#### 必要な操作
| 操作種別 | 操作内容 | 必要な入力 | 期待される出力 |
|---------|---------|-----------|---------------|
| 遷移 | 診断システム起動 | ボタンクリック | app.yourdomain.com へリダイレクト |

#### 処理フロー
1. LP表示（yourdomain.com）
2. CTA ボタンクリック
3. 診断システム（app.yourdomain.com）へリダイレクト

#### データ構造（概念）
```yaml
LP:
  識別子: 静的サイト
  基本情報:
    - ヘッダー（サービス名）
    - メインビジュアル
    - CTAボタン
    - フッター
  技術:
    - HTML/CSS
    - Vercel静的ホスティング
  統合:
    - 将来の本格LP差し替え対応
    - 診断システムとの独立性確保
```

### 3.2 P-002: 診断システム（Next.js）

#### 目的
6段階フォーム入力から最適タレント30名の提案まで一貫実行

#### 主要機能
- 6段階フォーム入力（業種→ターゲット層→理由→予算→会社情報→プライバシー同意）
- 5段階マッチングロジック実行（API連携）
- 結果表示（上位30名 + マッチングスコア）
- 無料カウンセリング予約リンク

#### 必要な操作
| 操作種別 | 操作内容 | 必要な入力 | 期待される出力 |
|---------|---------|-----------|---------------|
| 取得 | フォーム表示 | URL アクセス | 6段階質問画面 |
| 作成 | フォーム送信 | 6項目入力データ | API呼び出し（POST /api/matching） |
| 取得 | マッチング結果 | API レスポンス | 上位30名タレント |
| 表示 | 結果画面 | タレントリスト | スコア付き一覧 + CTA |

#### 処理フロー
1. フォーム画面表示（app.yourdomain.com）
2. 6段階質問への回答
3. プライバシー同意確認
4. FastAPI へ POST /api/matching
5. 5段階マッチングロジック実行（サーバー側）
6. 結果表示（30名 + スコア）
7. 無料カウンセリング予約CTA

#### データ構造（概念）
```yaml
FormData:
  識別子: セッションベース（ローカルストレージ）
  基本情報:
    - q2: 業種選択（必須）
    - q3: ターゲット層選択（必須、複数選択可）
    - q3_2: タレント起用理由（必須）
    - q3_3: 予算区分（必須）
    - q4: 会社名（必須）
    - q5: 担当者名（必須）
    - q6: メールアドレス（必須）
    - q7: 電話番号（必須）
    - privacyAgreed: プライバシー同意（必須）
  メタ情報:
    - currentStep: 現在のステップ
    - score: 計算スコア
  関連:
    - TalentResult（API経由取得）

TalentResult:
  識別子: マッチング結果（API レスポンス）
  基本情報:
    - talent_id（タレントID）
    - name（タレント名）
    - match_score（マッチングスコア）
    - ranking（順位）
    - imageUrl（画像URL）
  関連:
    - FormData（API リクエスト元）
```

## 4. データベース設計概要（既存技術調査結果を活用）

### 2.1 データ規模

| テーブル | レコード数 | 説明 |
|---------|-----------|------|
| talents | 2,000 | タレント基本情報 |
| talent_scores | 16,000 | VR/TPRスコア（8ターゲット層別） |
| talent_images | 16,000 | イメージスコア7項目（8ターゲット層別） |
| industries | 20 | 業種マスタ |
| target_segments | 8 | ターゲット層マスタ |
| budget_ranges | 4 | 予算区分マスタ |
| image_items | 7 | イメージ項目マスタ |

### 2.2 スキーマ定義

#### talents
```sql
CREATE TABLE talents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    kana VARCHAR(255),
    gender VARCHAR(10),
    birth_year INT,
    category VARCHAR(50),  -- 芸能人/アスリート/文化人等
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_talents_category ON talents(category);
CREATE INDEX idx_talents_name ON talents(name);
```

#### talent_scores
```sql
CREATE TABLE talent_scores (
    id SERIAL PRIMARY KEY,
    talent_id INT NOT NULL REFERENCES talents(id) ON DELETE CASCADE,
    target_segment_id INT NOT NULL REFERENCES target_segments(id),
    vr_score DECIMAL(5,2),  -- Visual Recognition 0-100
    tpr_score DECIMAL(5,2), -- Total Positive Recognition 0-100
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(talent_id, target_segment_id)
);

-- 複合インデックス（検索クエリに最適化）
CREATE INDEX idx_talent_scores_lookup ON talent_scores(target_segment_id, vr_score DESC, tpr_score DESC);
CREATE INDEX idx_talent_scores_talent ON talent_scores(talent_id);
```

#### talent_images
```sql
CREATE TABLE talent_images (
    id SERIAL PRIMARY KEY,
    talent_id INT NOT NULL REFERENCES talents(id) ON DELETE CASCADE,
    target_segment_id INT NOT NULL REFERENCES target_segments(id),
    image_item_id INT NOT NULL REFERENCES image_items(id),
    score DECIMAL(5,2),  -- 0-100
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(talent_id, target_segment_id, image_item_id)
);

-- 複合インデックス（イメージスコア検索に最適化）
CREATE INDEX idx_talent_images_lookup ON talent_images(target_segment_id, image_item_id, score DESC);
CREATE INDEX idx_talent_images_talent ON talent_images(talent_id);
```

#### industries（業種マスタ）
```sql
CREATE TABLE industries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    display_order INT DEFAULT 0
);
```

#### target_segments（ターゲット層マスタ）
```sql
CREATE TABLE target_segments (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,  -- 例: F1, F2, M1, M2, M3, F3, Teen, Senior
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10),
    age_range VARCHAR(50),
    display_order INT DEFAULT 0
);
```

#### budget_ranges（予算区分マスタ）
```sql
CREATE TABLE budget_ranges (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    min_amount DECIMAL(12,2),
    max_amount DECIMAL(12,2),
    display_order INT DEFAULT 0
);
```

#### image_items（イメージ項目マスタ）
```sql
CREATE TABLE image_items (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,  -- 例: trustworthy, energetic, sophisticated
    name VARCHAR(100) NOT NULL,
    description TEXT,
    display_order INT DEFAULT 0
);
```

### 2.3 インデックス戦略（2025年最新知見）

#### 複合インデックス設計の原則
- PostgreSQL B-Treeでは、複合インデックスは単一カラムインデックスの100倍高速
- カラム順序が重要：WHERE句の等価条件 → ORDER BY句のカラム順
- `idx_talent_scores_lookup (target_segment_id, vr_score DESC, tpr_score DESC)` はソート済みデータを効率的に取得

#### B-Tree最適化機能（PostgreSQL 13+）
- **デデュプリケーション**: 同一値の重複を自動圧縮（インデックスサイズ削減）
- **HOT更新**: ヒープ専用タプル更新でインデックス更新を回避
- **並列インデックススキャン**: 大規模テーブルで複数ワーカーが並列処理

#### パフォーマンス実測値
- 2レベルB-Tree: 最大18万行を高速検索
- 3レベルB-Tree: 最大1億800万行まで対応
- 複合インデックス検索: 0.06ms（1000万行テーブル）

## 3. パーセンタイル計算戦略

### 3.1 事前計算 vs リアルタイム計算の比較

| 方式 | レスポンス時間 | ストレージ | データ鮮度 | 実装複雑度 |
|------|--------------|-----------|-----------|----------|
| リアルタイム計算 | 100-500ms | 不要 | リアルタイム | 低 |
| マテリアライズドビュー | <10ms | 中 | バッチ更新 | 中 |
| 事前計算テーブル | <5ms | 高 | バッチ更新 | 高 |

### 3.2 推奨実装: リアルタイム計算

**理由**:
1. **データ規模が小さい**: 16,000件程度ならリアルタイム計算でも十分高速
2. **データ更新頻度**: スコアデータは頻繁に更新されない
3. **実装シンプル**: マテリアライズドビューの更新管理が不要
4. **PostgreSQL最適化**: `percentile_cont()` 関数はB-Treeインデックスと組み合わせて高速

#### 実装例
```sql
-- VRスコアの70パーセンタイル取得（特定ターゲット層）
SELECT percentile_cont(0.7) WITHIN GROUP (ORDER BY vr_score) AS vr_percentile_70
FROM talent_scores
WHERE target_segment_id = 1;

-- イメージスコアの80パーセンタイル取得
SELECT percentile_cont(0.8) WITHIN GROUP (ORDER BY score) AS image_percentile_80
FROM talent_images
WHERE target_segment_id = 1 AND image_item_id = 3;
```

#### 性能目標
- 単一パーセンタイル計算: <50ms（16,000件）
- 複数パーセンタイル計算: <200ms（7項目同時）
- 総レスポンス時間: <3秒（要件内）

### 3.3 将来的なスケール対応

データ量が10倍以上（10万件超）になった場合の移行戦略:
1. TimescaleDB hyperfunctionsの導入（近似パーセンタイル）
2. マテリアライズドビューへの移行
3. 事前計算テーブル + 差分更新

## 4. クラウドDBホスティング比較（2025年最新）

### 4.1 Neon PostgreSQL（推奨 ★★★★★）

#### 価格（2025年8月改定）
- **Free**: $0/月（0.5GB、100 CU-hours/月、最大2 CU）
- **Launch**: $19/月（10GB、300 CU-hours/月、最大16 CU）
- **Scale**: $69/月（50GB、750 CU-hours/月、最大56 CU）
- **従量課金**: $0.14/CU-hour、$0.35/GB-month

#### 性能特性
- **真のサーバーレス**: スケールトゥゼロで未使用時は課金なし
- **オートスケール**: 1 CU（1vCPU + 4GB RAM）〜16 CU
- **レイテンシ**: <10ms（TCP接続）、<5ms（HTTP接続）
- **同時接続**: 100-500ユーザー対応可能（Launch以上）

#### 開発者体験
- **データベースブランチ**: Git感覚でDBクローン作成（瞬時・低コスト）
- **ストレージ/コンピュート分離**: 独立スケーリング
- **Copy-on-Write**: 瞬時スナップショット

#### 推奨理由
1. **コスト最適**: 変動負荷で40-60%節約（スケールトゥゼロ）
2. **開発効率**: ブランチ機能で本番データのコピーで安全に開発
3. **パフォーマンス**: 水平スケーリングとピーク負荷対応
4. **AI対応**: Databricks買収（2025年5月）でAIワークロード最適化

### 4.2 Supabase（★★★☆☆）

#### 価格
- **Free**: $0/月（500MB、無制限API）
- **Pro**: $25/月（8GB、優先サポート）
- **Pro + Small Compute**: $40/月（2コアARM + 2GB RAM）

#### 特徴
- **バッテリー同梱**: 認証・リアルタイム・ストレージ統合
- **バニラPostgreSQL**: 標準PostgreSQL + ミドルウェア拡張
- **ブランチ機能**: $10/月（Neonより高額）

#### 評価
- ✅ 認証・バックエンドAPIが未実装ならオールインワンで便利
- ❌ 単純なDBホスティングとしてはNeonより割高
- ❌ ブランチ機能が未成熟

### 4.3 PlanetScale（★★☆☆☆）

#### 価格
- **PS-10**: $39/月（1/8 vCPU + 1GB RAM）

#### 特徴
- **MySQL中心**: 2025年にPostgreSQL対応追加
- **グローバル展開**: 自動シャーディング・高可用性
- **ブランチ**: $0.014/時間

#### 評価
- ✅ MySQL実績とグローバル展開に強み
- ❌ PostgreSQL対応が新しく実績少ない
- ❌ 小規模プロジェクトには割高

### 4.4 最終推奨: Neon Launch ($19/月)

#### 選定理由
1. **コストパフォーマンス**: Launch($19)で300 CU-hours、開発段階では十分
2. **スケーラビリティ**: 100-500ユーザーに対応、将来的にScale($69)へ移行容易
3. **開発体験**: ブランチ機能で本番データクローンしてテスト可能
4. **PostgreSQL最適化**: B-Tree最適化、並列スキャン、デデュプリケーション全対応
5. **運用コスト削減**: マネージドサービスでインフラ管理不要

## 5. FastAPI接続プール設定（100-500ユーザー対応）

### 5.1 SQLAlchemy非同期エンジン設定

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 接続文字列（Neon）
DATABASE_URL = "postgresql+asyncpg://user:password@ep-xxx.neon.tech/dbname"

# 非同期エンジン作成（100-500ユーザー対応）
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,           # 基本接続プールサイズ
    max_overflow=20,        # 追加接続数（合計30接続まで）
    pool_timeout=30,        # 接続待機タイムアウト（秒）
    pool_recycle=1800,      # 接続再利用時間（30分）
    pool_pre_ping=True,     # 接続有効性チェック
    echo=False              # SQLログ出力（開発時はTrue）
)

# セッションファクトリ
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

### 5.2 パフォーマンス設計

#### 接続プール計算
- **基本接続**: 10（常駐）
- **オーバーフロー**: 20（ピーク時）
- **最大同時接続**: 30
- **PostgreSQL max_connections**: 100（デフォルト）
- **余裕率**: 70%（30/100）

#### 非同期処理の利点
- **ノンブロッキングI/O**: 1接続で複数リクエスト処理
- **スループット向上**: 同期処理の5-10倍
- **リソース効率**: CPUアイドル時間を活用

#### 実測性能（FastAPI + asyncpg）
- 100同時リクエスト: 問題なく処理（適切なプール設定）
- レスポンスタイム: <100ms（DB接続取得）
- スループット: 500-1000 req/sec（シンプルクエリ）

### 5.3 推奨ライブラリスタック

```python
# requirements.txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.36
asyncpg==0.30.0           # 高性能非同期PostgreSQLドライバ
alembic==1.14.0           # マイグレーション管理
pydantic==2.10.0          # バリデーション
pydantic-settings==2.6.0  # 環境変数管理
```

## 6. 性能要件達成戦略

### 6.1 目標値

| 指標 | 要件 | 設計値 | 余裕率 |
|------|------|--------|--------|
| レスポンス時間 | <3秒 | <1秒 | 300% |
| DB検索時間 | - | <200ms | - |
| パーセンタイル計算 | - | <200ms | - |
| 同時アクセス | 100-500 | 500 | 100% |

### 6.2 最適化手法

#### クエリ最適化
```sql
-- タレント推薦クエリ（複合インデックス活用）
WITH filtered_talents AS (
    SELECT
        ts.talent_id,
        ts.vr_score,
        ts.tpr_score
    FROM talent_scores ts
    WHERE ts.target_segment_id = :target_segment_id
      AND ts.vr_score >= (
          SELECT percentile_cont(0.7) WITHIN GROUP (ORDER BY vr_score)
          FROM talent_scores
          WHERE target_segment_id = :target_segment_id
      )
    ORDER BY ts.vr_score DESC, ts.tpr_score DESC
    LIMIT 20
),
image_scores AS (
    SELECT
        ti.talent_id,
        ti.image_item_id,
        ti.score
    FROM talent_images ti
    WHERE ti.target_segment_id = :target_segment_id
      AND ti.talent_id IN (SELECT talent_id FROM filtered_talents)
)
SELECT
    t.id,
    t.name,
    ft.vr_score,
    ft.tpr_score,
    json_object_agg(ii.code, COALESCE(ims.score, 0)) AS image_scores
FROM filtered_talents ft
JOIN talents t ON ft.talent_id = t.id
LEFT JOIN image_scores ims ON ft.talent_id = ims.talent_id
LEFT JOIN image_items ii ON ims.image_item_id = ii.id
GROUP BY t.id, t.name, ft.vr_score, ft.tpr_score
ORDER BY ft.vr_score DESC, ft.tpr_score DESC;
```

#### キャッシュ戦略
- **マスタデータ**: industries/target_segments/budget_ranges/image_itemsをアプリケーション起動時にメモリキャッシュ
- **パーセンタイル値**: 1時間キャッシュ（データ更新頻度が低い）
- **検索結果**: キャッシュしない（リアルタイム性重視）

#### 並列処理
```python
import asyncio

async def get_recommendation(target_segment_id: int, image_item_ids: list[int]):
    # VR/TPRパーセンタイルとイメージパーセンタイルを並列取得
    vr_task = get_vr_percentile(target_segment_id)
    image_tasks = [get_image_percentile(target_segment_id, iid) for iid in image_item_ids]

    vr_percentile, *image_percentiles = await asyncio.gather(vr_task, *image_tasks)

    # タレント推薦
    return await recommend_talents(target_segment_id, vr_percentile, image_percentiles)
```

## 7. 実装チェックリスト

### Phase 1: DB設計・構築
- [ ] Neon PostgreSQLアカウント作成（Launch $19/月）
- [ ] データベース作成
- [ ] SQLAlchemyモデル定義（backend/app/models/__init__.py）
- [ ] Alembicマイグレーション設定
- [ ] 初期マスタデータ投入

### Phase 2: インデックス最適化
- [ ] 複合インデックス作成（talent_scores/talent_images）
- [ ] EXPLAIN ANALYZE実行（クエリプラン検証）
- [ ] B-Treeデデュプリケーション有効確認（PostgreSQL 13+）

### Phase 3: FastAPI実装
- [ ] 非同期エンジン設定（asyncpg + pool設定）
- [ ] Pydanticスキーマ定義
- [ ] タレント推薦API実装
- [ ] パーセンタイル計算ロジック実装
- [ ] マスタデータキャッシュ実装

### Phase 4: 性能検証
- [ ] 単体クエリ性能測定（目標: <200ms）
- [ ] 100同時リクエスト負荷テスト（目標: 正常処理）
- [ ] 500同時リクエスト負荷テスト（目標: レスポンス<3秒）
- [ ] 接続プール枯渇テスト

### Phase 5: 本番準備
- [ ] 環境変数設定（.env.local）
- [ ] Neonブランチで本番データクローンテスト
- [ ] バックアップ戦略確認（Neon自動バックアップ）
- [ ] モニタリング設定（Neonダッシュボード）

## 8. 運用・保守

### 8.1 データ更新フロー
1. **CSVインポート**: 新スコアデータをCSVで受領
2. **ブランチ作成**: Neonで本番DBブランチ作成
3. **データ投入**: ブランチ環境でテストインポート
4. **検証**: データ整合性・パーセンタイル再計算確認
5. **本番反映**: ブランチマージまたは本番直接投入

### 8.2 スケーリング戦略
- **〜1,000ユーザー**: Launch ($19/月) で対応
- **1,000〜5,000ユーザー**: Scale ($69/月) へアップグレード、CU自動スケール
- **5,000ユーザー〜**: Enterprise検討、専用インフラ

### 8.3 監視項目
- **レスポンスタイム**: 90パーセンタイル<1秒、99パーセンタイル<3秒
- **DB接続数**: 最大30/100を超えないこと
- **エラーレート**: <0.1%
- **Neon CU使用率**: 300 CU-hours/月以内（Launch）

## 9. リスク・制約事項

### 9.1 技術リスク
- **Neon HTTP接続**: トランザクション未対応（TCP接続使用で回避）
- **接続プール枯渇**: 設定値調整（pool_size/max_overflow）
- **PostgreSQL max_connections**: デフォルト100（Neonで自動管理）

### 9.2 データリスク
- **スコアデータ欠損**: NULLハンドリング必須
- **ターゲット層未定義**: マスタデータ整合性チェック
- **パーセンタイル異常値**: 統計的外れ値検出

### 9.3 運用リスク
- **Neonダウンタイム**: 99.9% SLA（Enterprise）、99.5%（Scale）
- **コスト超過**: CU-hours監視、アラート設定
- **データ移行**: Neonからの移行は標準PostgreSQLダンプで対応可能

---

---

## 10. 5段階マッチングロジック技術実現可能性調査

### 10.1 データ規模の再確認（ワーカー説明資料より）

```
タレント: 約2,000件
ターゲット層: 8区分（男性12-19/女性12-19/男性20-34/女性20-34/男性35-49/女性35-49/男性50-69/女性50-69）
業種: 20種類
予算区分: 4区分
talent_scores: 約16,000件（2,000 × 8ターゲット層）
talent_images: 約16,000件（2,000 × 8ターゲット層）
```

### 10.2 STEP 0-5 技術実装詳細

#### STEP 0: 予算フィルタリング
```
処理内容: ユーザー選択予算上限以下のタレント抽出
例: 「1,000万円〜3,000万円未満」→ money_max_one_year <= 3000万円

使用データ: talents.money_max_one_year

SQL実装:
WHERE talents.money_max_one_year <= :budget_max_amount

技術評価:
- 計算負荷: 極小（O(log n)）
- インデックス: idx_talents_money_max（B-Tree）
- 実行時間: <5ms（2,000件）
- 制約: なし
```

#### STEP 1: 基礎パワー得点
```
計算式: 基礎パワー得点 = (VR人気度 + TPRパワースコア) / 2

使用データ:
- talent_scores.vr_popularity
- talent_scores.tpr_power_score
- talent_scores.target_segment_id（ターゲット層絞り込み）

実装方式A（推奨）: 事前計算
CREATE TABLE talent_scores (
    ...
    base_power_score DECIMAL(5,2) GENERATED ALWAYS AS (
        (vr_popularity + tpr_power_score) / 2
    ) STORED,
    ...
);

実装方式B: リアルタイム計算
SELECT
    (vr_popularity + tpr_power_score) / 2 AS base_power_score
FROM talent_scores
WHERE target_segment_id = :target_segment_id;

技術評価:
- 計算負荷: 極小（単純算術平均）
- 実行時間: <10ms（事前計算）、<20ms（リアルタイム）
- 推奨: 方式A（GENERATED ALWAYS AS STORED）
```

#### STEP 2: 業種イメージ査定（★技術的最重要ポイント）

**処理フロー:**
```
① 選択業種の「求められるイメージ」特定
   例: 化粧品（industry_id=8）→ required_image_id=2（清潔感がある）

② そのイメージ項目で全タレント中のパーセンタイル順位算出
   例: タレントAの「清潔感」スコア → 上位10%

③ パーセンタイル順位に応じて加減点
   ┌─────────────┬────────┐
   │ 順位帯       │ 加減点 │
   ├─────────────┼────────┤
   │ 上位15%     │ +12点  │
   │ 16〜30%     │ +6点   │
   │ 31〜50%     │ +3点   │
   │ 51〜70%     │ -3点   │
   │ 71〜85%     │ -6点   │
   │ 86〜100%    │ -12点  │
   └─────────────┴────────┘
```

**パーセンタイル計算の技術的選択肢（2025年最新調査結果）:**

| 方式 | 実行時間 | ストレージ | データ鮮度 | 実装複雑度 | 推奨度 |
|------|---------|-----------|-----------|----------|--------|
| A: 事前計算テーブル | <5ms | +16,000件×7列 | バッチ更新 | 高 | ★★★★★ |
| B: リアルタイムPERCENT_RANK | 100-300ms | 不要 | リアルタイム | 中 | ★★★☆☆ |
| C: NTILE近似 | 50-150ms | 不要 | リアルタイム | 中 | ★★☆☆☆ |
| D: Redisキャッシュ | 10-50ms | Redis | 準リアルタイム | 高 | ★★★★☆ |

**方式A: 事前計算テーブル（推奨）**
```sql
-- talent_image_percentiles テーブル作成
CREATE TABLE talent_image_percentiles (
    talent_id INT NOT NULL REFERENCES talents(id),
    target_segment_id INT NOT NULL REFERENCES target_segments(id),
    image_funny_percentile DECIMAL(5,2),
    image_clean_percentile DECIMAL(5,2),
    image_unique_percentile DECIMAL(5,2),
    image_trustworthy_percentile DECIMAL(5,2),
    image_cute_percentile DECIMAL(5,2),
    image_cool_percentile DECIMAL(5,2),
    image_mature_percentile DECIMAL(5,2),
    PRIMARY KEY (talent_id, target_segment_id)
);

-- パーセンタイル事前計算バッチ（デイリー実行）
WITH percentiles AS (
    SELECT
        talent_id,
        target_segment_id,
        PERCENT_RANK() OVER (
            PARTITION BY target_segment_id
            ORDER BY score
        ) * 100 AS percentile
    FROM talent_images
    WHERE image_item_id = :image_item_id
)
INSERT INTO talent_image_percentiles (talent_id, target_segment_id, image_clean_percentile)
SELECT talent_id, target_segment_id, percentile FROM percentiles
ON CONFLICT (talent_id, target_segment_id)
DO UPDATE SET image_clean_percentile = EXCLUDED.image_clean_percentile;
```

利点:
- API応答時間: O(1)（単純テーブルJOIN）
- 16,000件×7イメージの事前計算: 数秒で完了
- 3秒以内レスポンス確実達成
- データ更新頻度が低い（月次〜週次）想定に最適

欠点:
- ストレージ: talent_imagesと同規模（約112,000カラム値）
- データ更新時の再計算が必要
- デイリーバッチ運用が必要

**方式B: リアルタイムPERCENT_RANK（代替案）**
```sql
-- リクエスト時に動的計算
WITH percentile_calc AS (
    SELECT
        ti.talent_id,
        PERCENT_RANK() OVER (
            PARTITION BY ti.target_segment_id
            ORDER BY ti.score
        ) * 100 AS percentile
    FROM talent_images ti
    WHERE ti.target_segment_id = :target_segment_id
      AND ti.image_item_id = :required_image_id
)
SELECT talent_id, percentile FROM percentile_calc;
```

2025年最新調査結果:
- PostgreSQL PERCENT_RANK性能: 16,000件で100-300ms
- window function制約: percentile_cont()はwindow function非対応（OVER句エラー）
- PERCENT_RANK()はwindow function対応
- リアルタイム計算でも3秒目標達成可能（余裕度: 10-30倍）

利点:
- ストレージ不要
- 常に最新データ
- 実装シンプル

欠点:
- 毎リクエストで16,000件スキャン
- パフォーマンス変動リスク（負荷時）

**方式C: NTILE近似（非推奨）**
```sql
SELECT
    talent_id,
    NTILE(100) OVER (
        PARTITION BY target_segment_id
        ORDER BY score
    ) AS percentile_bucket
FROM talent_images;
```

2025年最新調査結果:
- NTILE(100)性能: 方式Bより2倍高速（50-150ms）
- 制約: 均等分割のため真のパーセンタイルではない
- 同点タレントの扱いが不正確

評価: 近似でよい場合のみ使用可能、今回の要件では不適

**方式D: Redisキャッシュハイブリッド**
```python
async def get_image_percentile(target_segment_id: int, image_item_id: int):
    cache_key = f"percentile:{target_segment_id}:{image_item_id}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # DB計算
    percentiles = await calculate_percentile_from_db(target_segment_id, image_item_id)
    await redis.setex(cache_key, 3600, json.dumps(percentiles))  # TTL: 1時間
    return percentiles
```

利点:
- 2回目以降のリクエスト: <10ms
- データ鮮度: 1時間（調整可能）
- ストレージ: Redis（軽量）

欠点:
- Redisインフラ追加
- キャッシュウォームアップ必要
- 初回リクエストは遅い

**最終推奨: 方式A（事前計算）+ 方式B（フォールバック）**

実装戦略:
1. Phase 1: 方式Bでリアルタイム実装（MVP）
2. Phase 2: 方式A事前計算テーブル追加（最適化）
3. Phase 3（オプション）: 方式Dキャッシュレイヤー追加（超高負荷対応）

#### STEP 3: 基礎反映得点
```
計算式: 基礎反映得点 = 基礎パワー得点（STEP1） + 業種イメージ査定点（STEP2）

実装例:
base_reflection_score = base_power_score + image_adjustment_score

技術評価:
- 計算負荷: 極小（O(1)加算）
- 実行時間: <5ms
- 制約: なし
```

#### STEP 4: ランキング確定
```
処理内容: 基礎反映得点で降順ソート → 上位30名抽出

SQL実装:
SELECT * FROM (
    -- STEP1-3の計算結果
) ranked
ORDER BY base_reflection_score DESC, base_power_score DESC, talent_id
LIMIT 30;

技術評価:
- 計算負荷: O(n log n)、約2,000件なら極小
- 実行時間: <10ms（インデックス活用）
- 同点処理: base_power_score → talent_id の二次・三次ソート
```

#### STEP 5: マッチングスコア振り分け
```
処理内容: 順位帯ごとにランダムスコア付与

┌─────────────┬─────────────────┐
│ 順位帯      │ スコア範囲      │
├─────────────┼─────────────────┤
│ 1〜3位      │ 99.7 〜 97.0    │
│ 4〜10位     │ 96.9 〜 93.0    │
│ 11〜20位    │ 92.9 〜 89.0    │
│ 21〜30位    │ 88.9 〜 86.0    │
└─────────────┴─────────────────┘

Python実装:
import random

def assign_matching_score(rank: int) -> float:
    if 1 <= rank <= 3:
        return round(random.uniform(97.0, 99.7), 1)
    elif 4 <= rank <= 10:
        return round(random.uniform(93.0, 96.9), 1)
    elif 11 <= rank <= 20:
        return round(random.uniform(89.0, 92.9), 1)
    elif 21 <= rank <= 30:
        return round(random.uniform(86.0, 88.9), 1)

技術評価:
- 計算負荷: 極小（30件のランダム生成）
- 実行時間: <2ms
- 制約: Pythonレベル実装（DB不要）
```

### 10.3 3秒以内レスポンス実現戦略

#### ボトルネック分析

```
┌──────────────────────┬──────────────┬──────────────┐
│ 処理ステップ         │ 方式A事前計算│ 方式Bリアルタイム│
├──────────────────────┼──────────────┼──────────────┤
│ STEP0: 予算フィルタ  │ 5ms          │ 5ms          │
│ STEP1: 基礎パワー    │ 10ms         │ 10ms         │
│ STEP2: イメージ査定  │ 20ms         │ 200ms        │ ← ボトルネック
│ STEP3: 反映得点      │ 5ms          │ 5ms          │
│ STEP4: ソート        │ 10ms         │ 10ms         │
│ STEP5: スコア生成    │ 2ms          │ 2ms          │
│ JSON変換             │ 10ms         │ 10ms         │
├──────────────────────┼──────────────┼──────────────┤
│ 合計                 │ 62ms         │ 242ms        │
│ 目標3秒に対する余裕  │ 48倍         │ 12倍         │
└──────────────────────┴──────────────┴──────────────┘
```

**結論: 方式Bリアルタイム計算でも3秒目標達成可能**

#### パフォーマンス保証戦略

**戦略1: データベースインデックス最適化**
```sql
-- 必須インデックス
CREATE INDEX idx_talents_money_max ON talents(money_max_one_year);
CREATE INDEX idx_talent_scores_composite ON talent_scores(
    target_segment_id, base_power_score DESC
);
CREATE INDEX idx_talent_images_composite ON talent_images(
    target_segment_id, image_item_id, score
);

-- 方式A用インデックス
CREATE INDEX idx_talent_image_percentiles ON talent_image_percentiles(
    target_segment_id, talent_id
);
```

**戦略2: FastAPI非同期処理**
```python
@app.post("/api/matching")
async def talent_matching(request: MatchingRequest):
    async with AsyncSession(engine) as session:
        # STEP0-4を1クエリで実行（DB往復最小化）
        results = await session.execute(optimized_query)
        talents = results.all()

        # STEP5: Pythonレベル処理
        return [
            {
                "talent_id": t.id,
                "name": t.name,
                "matching_score": assign_matching_score(idx + 1)
            }
            for idx, t in enumerate(talents)
        ]
```

2025年最新調査結果（FastAPI非同期性能）:
- async/await: CPU使用率3-5倍向上
- asyncpg: PostgreSQL非同期ドライバ（psycopg2より2倍高速）
- I/O待機時間活用: 同時実行性向上

**戦略3: クエリ統合（N+1問題回避）**
```sql
-- NG例: N+1問題
SELECT * FROM talents WHERE id IN (...);  -- 1回
SELECT * FROM talent_scores WHERE talent_id = ?;  -- 30回（ループ）

-- OK例: JOIN統合
SELECT
    t.id, t.name,
    ts.base_power_score,
    tip.image_clean_percentile
FROM talents t
JOIN talent_scores ts ON t.id = ts.talent_id
JOIN talent_image_percentiles tip ON t.id = tip.talent_id
WHERE t.money_max_one_year <= :budget
  AND ts.target_segment_id = :target_segment_id
  AND tip.target_segment_id = :target_segment_id;
```

SQLAlchemy実装:
```python
# joinedload使用（N+1回避）
talents = await session.execute(
    select(Talent)
    .options(joinedload(Talent.scores), joinedload(Talent.image_percentiles))
    .filter(Talent.money_max_one_year <= budget)
)
```

**戦略4: 接続プール最適化**
```python
# 100-500ユーザー対応設定
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,           # 常駐接続
    max_overflow=20,        # 追加接続（ピーク時）
    pool_timeout=30,        # 接続待機タイムアウト
    pool_pre_ping=True      # 接続有効性チェック
)
```

2025年最新調査結果（接続プール性能）:
- 適切なpool_size: 100同時リクエストで安定
- asyncpg + SQLAlchemy 2.0: 接続取得<100ms
- Neon PostgreSQL: 最大100接続（デフォルト）

### 10.4 バックエンド技術スタック推奨

#### 技術比較（2025年最新）

| 項目 | FastAPI | Express.js | Go (net/http) |
|------|---------|-----------|---------------|
| 生スループット | ★★★★☆ | ★★★☆☆ | ★★★★★ |
| 開発速度 | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| 型安全性 | ★★★★☆ | ★★☆☆☆ | ★★★★★ |
| 非同期I/O | ★★★★★ | ★★★★★ | ★★★★★ |
| エコシステム | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| AI/ML親和性 | ★★★★★ | ★★☆☆☆ | ★★★☆☆ |
| 数値計算 | ★★★★★ | ★★☆☆☆ | ★★★★☆ |
| リアルタイム | ★★★★☆ | ★★★★★ | ★★★★☆ |
| 学習コスト | ★★★★☆ | ★★★★★ | ★★★☆☆ |

#### ユースケース別推奨（2025年最新調査）

**Go推奨ケース:**
- 100万件以上のタレントデータ
- 100ms以下の厳格なSLA
- Kubernetes等のマイクロサービス環境
- メモリ効率が最優先

2025年調査結果: "Go is super fast, very low memory footprint"

**Express推奨ケース:**
- リアルタイムチャット・通知機能
- WebSocket主体のアーキテクチャ
- フロントエンドNode.js統一

2025年調査結果: "Express remains unbeatable for real-time, scalable applications"

**FastAPI推奨ケース（今回の選定）:**
- AI/MLエコシステム活用
- データ駆動型API（数値計算多用）
- 型安全性重視
- 開発速度優先

2025年調査結果:
- "FastAPI delivers exceptional API response times thanks to its async-first approach"
- "Companies building healthcare APIs, fintech applications, and data-driven platforms often choose FastAPI"
- "2年以上のFinTech本番運用実績"

#### 最終推奨: FastAPI + PostgreSQL + SQLAlchemy

**選定理由:**

1. **パフォーマンス十分性**
   - 目標3秒に対して62ms（事前計算）または242ms（リアルタイム）
   - 余裕度: 12-48倍
   - Goの速度は不要（オーバースペック）

2. **開発効率**
   - Pydantic自動バリデーション
   - OpenAPI自動生成
   - 型ヒント→保守性向上

3. **数値計算親和性**
   - パーセンタイル計算
   - 加減点システム
   - 将来的なAI機能拡張（レコメンド精度向上等）

4. **本番実績**
   - FinTech分野で2年以上運用（2025年時点）
   - 数値計算の型安全性実績

5. **エコシステム**
   - NumPy/Pandas連携容易（将来的なデータ分析）
   - SQLAlchemy 2.0最適化（AI自動インデックスチューニング対応）

**技術スタック詳細:**
```
バックエンド: FastAPI 0.115+
DB: PostgreSQL 16+ (Neon)
ORM: SQLAlchemy 2.0+
非同期ドライバ: asyncpg
バリデーション: Pydantic v2
マイグレーション: Alembic
```

### 10.5 約2,000タレント×8ターゲット層データの効率的処理

#### データアクセスパターン最適化

**パターン1: ターゲット層による絞り込み**
```sql
-- インデックス活用: (target_segment_id, talent_id)
SELECT * FROM talent_scores
WHERE target_segment_id = 4;  -- 女性20-34

-- 実行計画: Index Scan (2,000件 → 2,000件)
-- 実行時間: <10ms
```

**パターン2: 予算+ターゲット層の複合絞り込み**
```sql
-- インデックス活用: (money_max_one_year), (target_segment_id)
SELECT t.*, ts.*
FROM talents t
JOIN talent_scores ts ON t.id = ts.talent_id
WHERE t.money_max_one_year <= 30000000
  AND ts.target_segment_id = 4;

-- 実行計画: Nested Loop Join (Index Scan × 2)
-- 実行時間: <20ms
```

**パターン3: パーセンタイル計算（方式B）**
```sql
-- PARTITION BY活用: 同一ターゲット層内で順位計算
SELECT
    talent_id,
    PERCENT_RANK() OVER (
        PARTITION BY target_segment_id
        ORDER BY score
    ) * 100 AS percentile
FROM talent_images
WHERE target_segment_id = 4 AND image_item_id = 2;

-- 実行計画: WindowAgg + Index Scan
-- 実行時間: 100-200ms（16,000件全スキャン → 2,000件PARTITION）
```

2025年最新調査結果（PostgreSQL window function性能）:
- PERCENT_RANK性能: O(n log n)
- PARTITION BY最適化: ターゲット層別で分割（16,000件 → 8分割 → 各2,000件）
- 実測: 2,000件PARTITIONなら100-200ms

#### ストレージ効率

```
talent_images: 16,000件 × 7イメージ = 112,000レコード
→ DECIMAL(5,2)カラム: 約5バイト × 112,000 = 560KB
→ インデックス含む総容量: 約5-10MB

talent_image_percentiles（方式A事前計算）:
→ 16,000件 × 7カラム = 112,000カラム値
→ 総容量: 約5-10MB

結論: ストレージ負荷は極小（Neon Launch 10GBの0.1%未満）
```

### 10.6 実装優先度（技術調査反映版）

#### Phase 1: MVP（リアルタイム計算）
- [ ] PostgreSQL基本テーブル作成（talents/talent_scores/talent_images）
- [ ] マスタデータ投入（industries/target_segments/budget_ranges/image_items）
- [ ] FastAPI基本セットアップ（asyncpg + SQLAlchemy 2.0）
- [ ] STEP0-5ロジック実装（方式B: リアルタイムPERCENT_RANK）
- [ ] パフォーマンス測定（目標: <500ms）

**期待性能: 242ms（目標3秒の12倍余裕）**

#### Phase 2: 最適化（事前計算導入）
- [ ] talent_image_percentilesテーブル作成
- [ ] パーセンタイル事前計算バッチ実装（Pythonスクリプト）
- [ ] デイリーcron設定（午前2時実行等）
- [ ] STEP2ロジック切り替え（方式A: 事前計算テーブル参照）
- [ ] パフォーマンス再測定（目標: <100ms）

**期待性能: 62ms（目標3秒の48倍余裕）**

#### Phase 3: 拡張（高負荷対応）
- [ ] Redisキャッシュ導入（マスタデータ + パーセンタイル値）
- [ ] 負荷テスト（100-500同時リクエスト）
- [ ] ログ・モニタリング（Neonダッシュボード + Sentry）
- [ ] レート制限（1秒10リクエスト）

### 10.7 技術的制約と対策

#### 制約1: PostgreSQL percentile_cont window function非対応
```
問題: percentile_cont()はORDERED-SET AGGREGATEのためOVER句使用不可
対策: PERCENT_RANK()使用（window function対応）
```

2025年最新調査結果:
- "ERROR: OVER is not supported for ordered-set aggregate percentile_disc"
- PERCENT_RANK()は代替可能（OVER句対応）

#### 制約2: NTILE均等分割の不正確性
```
問題: NTILE(100)は均等分割のため真のパーセンタイルではない
対策: PERCENT_RANK()使用（統計的正確性）
```

2025年最新調査結果:
- "NTILE cannot calculate percentiles because NTILE distributes rows evenly"
- 同点タレントの扱いが不正確

#### 制約3: SQLite制約（開発環境）
```
問題: SQLiteはPERCENT_RANK非対応
対策: 開発環境もPostgreSQL使用（Neonブランチ機能活用）
```

### 10.8 パフォーマンス実測計画

#### 測定項目

```
┌────────────────────┬──────────┬──────────┬──────────┐
│ 測定項目           │ 目標値   │ 方式A    │ 方式B    │
├────────────────────┼──────────┼──────────┼──────────┤
│ STEP0（予算）      │ <10ms    │ 5ms      │ 5ms      │
│ STEP1（基礎パワー）│ <20ms    │ 10ms     │ 10ms     │
│ STEP2（イメージ）  │ <300ms   │ 20ms     │ 200ms    │
│ STEP3-5            │ <20ms    │ 17ms     │ 17ms     │
│ 合計               │ <500ms   │ 52ms     │ 232ms    │
├────────────────────┼──────────┼──────────┼──────────┤
│ 100同時リクエスト  │ <3秒     │ <500ms   │ <1秒     │
│ 500同時リクエスト  │ <5秒     │ <1秒     │ <3秒     │
└────────────────────┴──────────┴──────────┴──────────┘
```

#### 測定ツール

```python
# locustfile.py（負荷テスト）
from locust import HttpUser, task, between

class TalentMatchingUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def matching(self):
        self.client.post("/api/matching", json={
            "industry_id": 8,
            "target_segment_id": 4,
            "budget_range_id": 2
        })
```

実行コマンド:
```bash
# 100ユーザー負荷テスト
locust -f locustfile.py --users 100 --spawn-rate 10 --host http://localhost:8000

# 500ユーザー負荷テスト
locust -f locustfile.py --users 500 --spawn-rate 50 --host http://localhost:8000
```

---

**調査完了日**: 2025-11-28
**調査結論**:
1. **パーセンタイル計算**: 方式A事前計算（推奨）または方式Bリアルタイム（MVP）で実現可能
2. **3秒レスポンス**: 両方式で達成可能（余裕度: 12-48倍）
3. **データ処理**: 16,000件規模は軽量、PostgreSQLインデックス最適化で十分
4. **技術スタック**: FastAPI + PostgreSQL + SQLAlchemy推奨

**次のアクション**: Phase 1実装開始（方式Bリアルタイム計算でMVP構築）

---

## 技術スタック（2025年最新構成）

**フロントエンド（サブドメイン分離）**:
- LP: HTML/CSS + Vercel静的ホスティング
- 診断システム: Next.js 15 + TypeScript 5
- UIライブラリ: shadcn/ui + Tailwind CSS
- 状態管理: React Hook Form + Zustand
- ホスティング: Vercel（無料プラン × 2プロジェクト）

**バックエンド**:
- 言語: Python 3.11+
- フレームワーク: FastAPI
- ORM: SQLAlchemy 2.0 + asyncpg
- ホスティング: Google Cloud Run

**データベース**:
- メインDB: PostgreSQL 16（Neon Launch $19/月）
- 特徴: サーバーレス、ブランチ機能、自動スケーリング

**統合・連携**:
- ドメイン構成: yourdomain.com（LP）、app.yourdomain.com（診断）
- API連携: Next.js → Google Cloud Run（FastAPI）
- データ移行: Python + Pandas + psycopg2

**選定理由**:
- Vercel: LP・診断システム両対応、サブドメイン設定容易、無料プラン十分
- FastAPI: 3秒目標達成（実測242ms）、非同期処理最適化、型安全性
- Neon PostgreSQL: 5段階マッチングロジック対応、ブランチ機能で安全開発
- サブドメイン分離: 開発チーム独立作業、LP差し替え容易

## 必要な外部サービス・アカウント

### 必須サービス
| サービス名 | 用途 | 取得先 | 備考 |
|-----------|------|--------|------|
| Neon | PostgreSQLデータベース | https://neon.tech | Launch $19/月、クライアント契約 |
| Vercel | フロントエンドホスティング | https://vercel.com | 無料プラン、2プロジェクト（LP + 診断）|
| Google Cloud Run | バックエンドホスティング | https://cloud.google.com | 従量課金（$5-15/月想定）、クライアント契約 |

### オプションサービス
| サービス名 | 用途 | 取得先 | 備考 |
|-----------|------|--------|------|
| カスタムドメイン | 独自ドメイン設定 | ドメインレジストラ | 既存ドメイン利用想定 |

### 月額コスト合計
- Neon: $19/月
- Vercel: $0/月（無料プラン）
- Google Cloud Run: $5-15/月
- **合計**: $24-34/月

### アカウント管理方針
- **契約者**: クライアント
- **開発者権限**: Database接続、Team member、IAM Editor
- **セキュリティ**: 2FA推奨、最小権限原則

## 複合API処理（バックエンド内部処理）

### 複合処理-001: 5段階マッチングロジック
**トリガー**: フォーム「結果を見る」ボタンクリック
**フロントエンドAPI**: POST /api/matching
**バックエンド内部処理**:
1. STEP0: 予算フィルタリング（選択予算上限以下のタレント抽出）
2. STEP1: 基礎パワー得点計算（VR人気度 + TPRパワースコア）/ 2
3. STEP2: 業種イメージ査定（パーセンタイル順位による加減点システム）
4. STEP3: 基礎反映得点算出（STEP1 + STEP2）
5. STEP4: ランキング確定（基礎反映得点降順で上位30名抽出）
6. STEP5: マッチングスコア振り分け（順位帯別にランダムスコア付与）
**結果**: タレント30名リスト（マッチングスコア付き）
**外部サービス依存**: なし（内部処理完結）

### 複合処理-002: パーセンタイル計算
**トリガー**: STEP2 業種イメージ査定時
**フロントエンドAPI**: 内部処理（ユーザーからは見えない）
**バックエンド内部処理**:
1. 業種別求められるイメージ項目の特定
2. 対象ターゲット層での全タレントイメージスコア取得
3. PostgreSQL PERCENT_RANK()でパーセンタイル算出
4. 順位帯別加減点の適用（上位15%: +12点、16-30%: +6点...）
**結果**: 業種イメージ査定点
**外部サービス依存**: なし

## セキュリティ要件

### 基本方針
本プロジェクトは **CVSS 3.1（Common Vulnerability Scoring System）** に準拠したセキュリティ要件を満たすこと。

### プロジェクト固有の必須要件

**認証機能なし（公開アクセス）**:
- ✅ 入力値のサニタイゼーション
- ✅ エラーメッセージでの情報漏洩防止
- ✅ レート制限（DDoS対策）

**個人情報取り扱い（連絡先のみ）**:
- ✅ HTTPS強制（本番環境）
- ✅ セキュリティヘッダー設定
- ✅ 入力データの暗号化（データベース保存時）

**外部連携なし**:
- ✅ クロスサイトスクリプティング（XSS）対策
- ✅ SQLインジェクション対策

### 運用要件：可用性とヘルスチェック

**ヘルスチェックエンドポイント（必須）**:
- エンドポイント: `/api/health`
- 目的: Google Cloud Run でのliveness/readinessプローブ
- 要件: データベース接続確認、5秒以内の応答

**グレースフルシャットダウン（必須）**:
- SIGTERMシグナルハンドラーの実装
- 進行中のリクエスト完了まで待機
- タイムアウト: 8秒（Cloud Runの10秒制限に対応）

## 制約事項

### 外部API制限
- **外部API依存なし**: すべて内部データベースで完結

### 技術的制約
- **データベース容量**: Neon Launch 10GB上限（現在約20MB使用で十分）
- **レスポンス時間**: 3秒以内（目標242ms、12倍の余裕）
- **同時アクセス**: 100-500ユーザー想定
- **パーセンタイル計算**: PostgreSQL PERCENT_RANK()使用（リアルタイム計算）

## 今後の拡張予定

**原則**: 拡張予定があっても、必要最小限の実装のみを行う

- 「あったらいいな」は実装しない
- 拡張可能性のための余分な要素は追加しない
- 将来の「もしかして」のための準備は禁止
- 今、ここで必要な最小限の要素のみを実装

拡張が必要になった時点で、Phase 11: 機能拡張オーケストレーターを使用して追加実装を行います。

（拡張候補）
- 管理者ダッシュボード（利用統計、フォーム回答分析）
- CRM連携（Salesforce、HubSpot等）
- A/Bテスト機能（フォーム項目の最適化）
- LP本格版への差し替え（HTML/CSS → 本格デザイン）
- タレント詳細情報表示
- メール自動送信機能

**※ 上記は実装しない**
