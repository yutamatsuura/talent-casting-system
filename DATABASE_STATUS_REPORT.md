# Neon PostgreSQL データベース状況レポート

実行日: 2025-12-03
対象: Neon PostgreSQL (neondb)

## データベース状況レポート

### 接続状況: ✅
- **接続先**: neondb
- **接続時間**: 1097.71ms
- **エラー**: なし
- **DATABASE_URL**: .env.localから正常に読み込み完了

### テーブル状況: 6/8 ⚠️

#### ✅ 存在するテーブル
- **budget_ranges** (カラム数: 6, レコード数: 4)
- **image_items** (カラム数: 4, レコード数: 7)
- **industries** (カラム数: 5, レコード数: 20)
- **talent_images** (カラム数: 11, レコード数: 8,000)
- **talent_scores** (カラム数: 10, レコード数: 32,032)
- **target_segments** (カラム数: 7, レコード数: 8)

#### ❌ 存在しないテーブル
- **talents** - 代わりに `m_account` テーブルが存在（4,819レコード）
- **industry_images** - 未作成

### 実際のテーブル構造（期待と異なる）

#### m_account テーブル（talentsの代替）
- **レコード数**: 4,819
- **主要カラム**:
  - `account_id` (integer) - PRIMARY KEY
  - `name_full_for_matching` (varchar) - タレント名
  - `birthday` (date)
  - `gender_type_cd` (integer)
  - `twitter_name`, `instagram_name`, `tiktok_name`, `youtube_channel_id`

#### m_talent_act テーブル（予算情報）
- **レコード数**: 3,224
- **主要カラム**:
  - `account_id` (integer)
  - `money_min_one_year` (予算下限)
  - `money_max_one_year` (予算上限) - 2,308件のデータあり
  - `cost_min_one_year`, `cost_max_one_year`

#### その他の関連テーブル
- m_talent_staff (4,232件)
- m_talent_media (4,305件)
- m_talent_deal (3,698件)
- m_talent_cm (6,687件)
- m_talent_other (4,487件)

### データ構造の問題点

1. **⚠️ テーブル名の相違**
   - 期待: `talents`
   - 実際: `m_account`

2. **⚠️ 予算情報の分離**
   - 予算情報が `m_talent_act` テーブルに分離されている
   - JOINが必要

3. **⚠️ industry_images テーブル不在**
   - 業種とイメージ項目の関連付けテーブルが未作成

4. **✅ account_id による一貫性**
   - すべてのテーブルが `account_id` をキーとして使用
   - 外部キー制約も適切に設定済み

### 5段階マッチングロジック実装可能性: ✅

- **STEP 0 (予算フィルタリング)**: ✅ 実装可能
  - m_talent_actテーブルのmoney_max_one_yearフィールド（2,308件）

- **STEP 1 (基礎パワー得点)**: ✅ 実装可能
  - talent_scoresテーブルにvr_popularity, tpr_power_score存在

- **STEP 2 (業種イメージ査定)**: ✅ 実装可能
  - talent_imagesテーブルに各イメージスコア存在
  - industriesテーブルにrequired_image_id存在

- **STEP 3-5 (得点計算・ランキング)**: ✅ 実装可能

### 推奨アクション

#### 1. 即座に実行すべき対応

```sql
-- talentsビューの作成（m_accountとm_talent_actを統合）
CREATE OR REPLACE VIEW talents AS
SELECT
    ma.account_id AS id,
    ma.account_id AS talent_id,
    ma.name_full_for_matching,
    ma.last_name,
    ma.first_name,
    ma.birthday,
    ma.gender_type_cd,
    ma.company_name,
    ma.twitter_name,
    ma.instagram_name,
    ma.tiktok_name,
    ma.youtube_channel_id,
    mta.money_min_one_year,
    mta.money_max_one_year,
    ma.created_at,
    ma.updated_at
FROM m_account ma
LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
WHERE ma.del_flag IS NULL OR ma.del_flag = 0;
```

#### 2. industry_imagesテーブルの作成

```sql
CREATE TABLE industry_images (
    industry_id INTEGER NOT NULL,
    image_id INTEGER NOT NULL,
    weight NUMERIC(5,2) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (industry_id, image_id),
    FOREIGN KEY (industry_id) REFERENCES industries(industry_id),
    FOREIGN KEY (image_id) REFERENCES image_items(image_id)
);
```

#### 3. コード修正の優先度

1. **高優先度**: SQLクエリで `talents` を `m_account` に置換（またはビュー作成）
2. **高優先度**: 予算フィルタリングで `m_talent_act` をJOIN
3. **中優先度**: `account_id` を `talent_id` としてエイリアス使用
4. **低優先度**: industry_images テーブルの初期データ投入

### データ整合性の確認結果: ✅

- talent_scores と m_account: **整合性OK** (orphan records: 0)
- talent_images と m_account: **整合性OK** (orphan records: 0)
- target_segments の範囲: ID 9-16 (男女×年齢4区分)

### 結論

データベース構造は**概ね期待通り**ですが、以下の調整が必要：

1. **テーブル名の差異は対応可能** - ビューまたはエイリアスで解決
2. **予算情報の分離は問題なし** - JOINで対応
3. **5段階マッチングロジックは完全実装可能**
4. **データ量も十分** - タレント4,819件、スコアデータ32,032件

**推奨**: 上記のビュー作成とindustry_imagesテーブル作成を実行後、実装に進むことができます。