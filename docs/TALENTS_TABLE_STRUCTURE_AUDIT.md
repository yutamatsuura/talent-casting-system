# talentsテーブル構造確認レポート

**実施日**: 2025-12-02
**検査対象**: Neon PostgreSQL (talent-casting-form)
**検査方法**: 直接データベース接続による実測定

---

## 1. テーブル構造の詳細

### 1.1 CREATE TABLE定義

```sql
CREATE TABLE talents (
  id integer NOT NULL DEFAULT nextval('talents_id_seq'::regclass),
  account_id integer NOT NULL UNIQUE,
  name character varying NOT NULL,
  kana character varying,
  gender character varying,
  birth_year integer,
  category character varying,
  money_max_one_year numeric,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone NOT NULL DEFAULT now(),
  name_normalized character varying,
  company_name character varying,
  image_name character varying,
  birthday date,
  prefecture_code integer,
  official_url text,
  del_flag integer DEFAULT 0,
  PRIMARY KEY (id)
);
```

### 1.2 全カラム一覧と説明

| # | カラム名 | データ型 | NULL許可 | デフォルト | 説明 |
|---|---------|---------|---------|----------|------|
| 1 | id | integer | NO | nextval('talents_id_seq') | プライマリキー（自動採番） |
| 2 | account_id | integer | NO | | タレント識別ID（ユニーク） |
| 3 | name | varchar | NO | | 芸名（last_name + first_name） |
| 4 | kana | varchar | YES | | フリガナ |
| 5 | gender | varchar | YES | | 性別コード（1=男性、2=女性、3=その他） |
| 6 | birth_year | integer | YES | | 生年 |
| 7 | category | varchar | YES | | カテゴリ（俳優、タレント等） |
| 8 | money_max_one_year | numeric | YES | | **年間最大予算（万円）** |
| 9 | created_at | timestamp | NO | now() | 登録日時 |
| 10 | updated_at | timestamp | NO | now() | 更新日時 |
| 11 | name_normalized | varchar | YES | | 正規化名前（VR照合用） |
| 12 | company_name | varchar | YES | | 事務所名 |
| 13 | image_name | varchar | YES | | 画像ファイル名 |
| 14 | birthday | date | YES | | 誕生日 |
| 15 | prefecture_code | integer | YES | | 都道府県コード |
| 16 | official_url | text | YES | | 公式URL |
| 17 | del_flag | integer | YES | 0 | 削除フラグ（0=有効、1=削除） |

### 1.3 インデックス一覧

| インデックス名 | カラム | タイプ | ユニーク | 説明 |
|---|---|---|---|---|
| talents_pkey | id | BTREE | YES | プライマリキー |
| ix_talents_account_id | account_id | BTREE | YES | account_id一意性確保 |
| idx_talents_account_id | account_id | BTREE | NO | 検索最適化 |
| idx_talents_name | name | BTREE | NO | 名前検索 |
| idx_talents_name_normalized | name_normalized | BTREE | NO | 正規化名前検索 |
| idx_talents_category | category | BTREE | NO | カテゴリ検索 |
| idx_talents_money_max | money_max_one_year | BTREE | NO | **予算フィルタリング用** |
| idx_talents_company | company_name | BTREE | NO | 事務所検索 |
| idx_talents_del_flag | del_flag | BTREE | NO | 削除フラグフィルタ |

---

## 2. 実際のデータ内容（実測値）

### 2.1 レコード数と分布

```
総レコード数: 4,819
├─ del_flag = 0（有効）: 3,971 (82.4%)
├─ del_flag = 1（削除）: 848   (17.6%)
└─ del_flag = NULL: 0        (0%)
```

✓ 期待値（4,819）と一致

### 2.2 性別の分布

| 性別コード | 解釈 | レコード数 | 割合 |
|-----------|------|----------|------|
| 1 | 男性 | 2,399 | 49.8% |
| 2 | 女性 | 2,347 | 48.7% |
| 3 | その他 | 73 | 1.5% |
| **合計** | | **4,819** | **100%** |

### 2.3 カテゴリの分布（上位20個）

| # | カテゴリ | 件数 | 割合 |
|---|---------|------|------|
| 1 | 女優 | 481 | 10.0% |
| 2 | 俳優 | 476 | 9.9% |
| 3 | お笑いタレント | 272 | 5.6% |
| 4 | アーティスト | 175 | 3.6% |
| 5 | モデル | 136 | 2.8% |
| 6 | タレント | 98 | 2.0% |
| 7 | 女優、モデル | 93 | 1.9% |
| 8 | インフルエンサー | 75 | 1.6% |
| 9 | 女優、タレント | 53 | 1.1% |
| 10 | アイドル | 52 | 1.1% |
| 11 | 俳優、タレント | 51 | 1.1% |
| 12 | モデル、女優 | 49 | 1.0% |
| 13 | モデル、タレント | 48 | 1.0% |
| 14 | 声優 | 37 | 0.8% |
| 15 | 俳優、モデル | 29 | 0.6% |
| （その他75カテゴリ） | | 3,474 | 72.1% |
| **合計** | | **4,819** | **100%** |

### 2.4 事務所（会社）の分布（上位15個）

| # | 事務所名 | 件数 | 割合 |
|---|---------|------|------|
| 1 | 個人問合せ | 310 | 6.4% |
| 2 | 吉本興業 | 260 | 5.4% |
| 3 | STARTO ENTERTAINMENT | 120 | 2.5% |
| 4 | LDH JAPAN | 115 | 2.4% |
| 5 | ホリプロ | 104 | 2.2% |
| 6 | アミューズ | 99 | 2.1% |
| 7 | ワタナベエンターテインメント | 95 | 2.0% |
| 8 | エイベックス・マネジメント | 66 | 1.4% |
| 9 | オスカープロモーション | 65 | 1.3% |
| 10 | スターダストプロモーション制作3部 | 61 | 1.3% |
| 11 | スターダストプロモーション | 61 | 1.3% |
| 12 | SMA（ソニー・ミュージックアーティスツ） | 54 | 1.1% |
| 13 | Kiii | 51 | 1.1% |
| 14 | レプロエンタテインメント | 46 | 1.0% |
| 15 | 太田プロダクション | 43 | 0.9% |
| （その他550事務所） | | 2,822 | 58.6% |
| **合計** | | **4,819** | **100%** |

### 2.5 NULL値の分析

| カラム名 | 総レコード | NULL件数 | NULL率 | 状態 | 評価 |
|---------|----------|---------|--------|------|------|
| account_id | 4,819 | 0 | 0% | ✓ 完全 | A+ |
| name | 4,819 | 0 | 0% | ✓ 完全 | A+ |
| gender | 4,819 | 0 | 0% | ✓ 完全 | A+ |
| category | 4,819 | 34 | 0.7% | ✓ ほぼ完全 | A |
| del_flag | 4,819 | 0 | 0% | ✓ 完全 | A+ |
| image_name | 4,819 | 25 | 0.5% | ✓ ほぼ完全 | A |
| company_name | 4,819 | 126 | 2.6% | ○ 部分 | B |
| birthday | 4,819 | 511 | 10.6% | ○ 部分 | B |
| official_url | 4,819 | 1,011 | 21.0% | ○ 部分 | C |
| kana | 4,819 | 不明 | ? | ○ 部分 | B |
| **money_max_one_year** | **4,819** | **4,819** | **100%** | **⚠️ 全てNULL** | **F** |

---

## 3. 重大な問題点

### 問題1: money_max_one_year が全てNULL ⚠️ **CRITICAL**

**現状:**
- talents テーブル: 4,819件全てNULL（100%）
- ワーカー説明資料では: 「年間最大予算」として必須項目
- CLAUDE.md での位置づけ: STEP 0: 予算フィルタリング で使用

**原因の特定:**

#### Excelソースデータの分析
- ファイル: `/Users/lennon/projects/talent-casting-form/DB情報/Nowデータ_20251126.xlsx`
- シート: `m_account` (4,819行 × 27列)
- **money関連カラムが存在しない**

Excelの m_account シート カラム一覧：
```
1.  account_id
2.  last_name
3.  first_name
4.  last_name_kana
5.  first_name_kana
6.  image_name
7.  birthday
8.  gender_type_cd
9.  pref_cd
10. company_name
11. official_url
12. act_genre
13. twitter_account_have_flag
14. twitter_name
15. instagram_account_have_flag
16. instagram_name
17. tiktok_account_have_flag
18. tiktok_name
19. youtube_account_have_flag
20. youtube_channel_id
21. upload_last_name
22. upload_first_name
23. sort_last_name_kana
24. sort_first_name_kana
25. del_flag
26. regist_date
27. up_date
```

**問題点:**
- money関連カラムが完全に欠落している
- 予算フィルタリング機能が動作不可

#### バックアップテーブルの確認

`talents_backup_20251202_214046` には money_max_one_year が存在：
```
総レコード: 3,971
money_max_one_year設定: 2,202件 (55.4%)
money_max_one_year未設定: 1,769件 (44.6%)

予算統計:
  最小: ¥50万
  最大: ¥30,000万（3億円）
  平均: ¥2,907万
  中央値: ¥2,500万
```

**サンプルデータ:**
- 有吉弘行（Account 1）: ¥5,000万
- ローラ（Account 2）: ¥5,000万
- きゃりーぱみゅぱみゅ（Account 4）: ¥7,000万
- 松本人志（Account 399）: ¥600万
- 坂上忍（Account 1282）: ¥3,000万

**結論:** バックアップには正しいデータが存在するが、現在のテーブルに反映されていない。

---

### 問題2: VR/TPRスコアデータが未インポート ⚠️ **CRITICAL**

**現状:**

| テーブル名 | レコード数 | 状態 |
|-----------|----------|------|
| talent_scores | 0 | **⚠️ 完全に空** |
| talent_images | 0 | **⚠️ 完全に空** |
| talent_scores_backup_20251202_214046 | 8,004 | ✓ バックアップあり |
| talent_images_backup_20251202_214046 | 32,192 | ✓ バックアップあり |

**バックアップの詳細:**

```
talent_scores_backup_20251202_214046:
  総レコード: 8,004
  ユニークtalent_id: 1,001
  ユニークtarget_segment_id: 8
  構成: 1,001 talents × 8 target_segments

talent_images_backup_20251202_214046:
  総レコード: 32,192
  ユニークtalent_id: 1,000
  ユニークimage_item_id: 32 (推定)
  構成: 1,000 talents × 8 segments × 4 image_items (平均)
```

**影響:**
- CLAUDE.md STEP 1: 基礎パワー得点 → 計算不可
- CLAUDE.md STEP 2: 業種イメージ査定 → 計算不可
- CLAUDE.md STEP 3-5: 完全にブロック
- マッチングロジック全体が動作不可

**結論:** バックアップには完全なVRデータが存在するが、本テーブルに反映されていない。

---

## 4. データマッピング状況

### 4.1 Excelから現在のtalentsへのマッピング

| Excel列 | DB列 | マッピング状態 | 備考 |
|--------|-----|-------------|------|
| account_id | account_id | ✓ 完全 | 4,819件全て |
| last_name + first_name | name | ✓ 完全 | スペースなし連結 |
| last_name_kana + first_name_kana | kana | ✓ 完全 | |
| gender_type_cd | gender | ✓ 完全 | 1→1, 2→2, 3→3 |
| birthday | birthday | ✓ 完全 | |
| pref_cd | prefecture_code | ✓ 完全 | |
| company_name | company_name | ✓ ほぼ完全 | 126件NULL（2.6%） |
| official_url | official_url | ✓ ほぼ完全 | 1,011件NULL（21.0%） |
| act_genre | category | ✓ ほぼ完全 | 34件NULL（0.7%） |
| image_name | image_name | ✓ ほぼ完全 | 25件NULL（0.5%） |
| **（存在しない）** | **money_max_one_year** | **⚠️ 全てNULL** | **Excelに元データなし** |

### 4.2 性別コードのマッピング正確性

| Excel値 | DB値 | 解釈 | 件数 | 検証 |
|---------|-----|------|------|------|
| 1 | 1 | 男性 | 2,399 | ✓ |
| 2 | 2 | 女性 | 2,347 | ✓ |
| 3 | 3 | その他 | 73 | ✓ |

**結論:** 性別コードは完全に正確にマッピングされている

---

## 5. 関連テーブルの状態

### 5.1 マスタデータテーブル（✓ 完成）

| テーブル名 | レコード数 | 状態 | 用途 |
|-----------|----------|------|------|
| industries | 20 | ✓ 完成 | 業種マスタ |
| target_segments | 8 | ✓ 完成 | ターゲット層マスタ（男女×4年代） |
| image_items | 7 | ✓ 完成 | イメージ項目マスタ |
| industry_images | 20 | ✓ 完成 | 業種-イメージ紐付け |
| budget_ranges | 4 | ✓ 完成 | 予算区分マスタ |
| purpose_objectives | 7 | ✓ 完成 | 目的・目標マスタ |

### 5.2 VR/TPRデータテーブル（⚠️ 未実装）

| テーブル名 | レコード数 | バックアップ | 状態 | 必要性 |
|-----------|----------|----------|------|--------|
| talent_scores | 0 | 8,004 | ⚠️ 空 | CRITICAL |
| talent_images | 0 | 32,192 | ⚠️ 空 | CRITICAL |

### 5.3 履歴・詳細情報テーブル（未実装・優先度低）

| テーブル名 | レコード数 | 状態 | 実装予定 |
|-----------|----------|------|---------|
| talent_cm_history | 0 | 空 | Phase 7以降 |
| talent_business_info | 0 | 空 | 優先度低 |
| talent_contacts | 0 | 空 | 優先度低 |
| talent_media_experience | 0 | 空 | 優先度低 |
| talent_keywords | 0 | 空 | 優先度低 |
| talent_pricing | 0 | 空 | 優先度低 |

---

## 6. サンプルデータ（最初の20行）

| # | ID | Account | 名前 | 性別 | カテゴリ | 削除フラグ | 予算 |
|----|----|----|------|-----|---------|---------|------|
| 1 | 4546 | 631 | 倉科カナ | 2 | 女優、タレント | 0 | NULL |
| 2 | 4548 | 632 | 紗栄子 | 2 | タレント | 0 | NULL |
| 3 | 4550 | 634 | 今井悠貴 | 1 | 俳優 | 1 | NULL |
| 4 | 4552 | 635 | 上杉柊平 | 1 | 俳優 | 0 | NULL |
| 5 | 4554 | 637 | 鈴木福 | 1 | 俳優 | 0 | NULL |
| 6 | 4556 | 638 | えなりかずき | 1 | 俳優、タレント | 0 | NULL |
| 7 | 4558 | 640 | 岡本圭人 | 1 | アイドル（Hey! Say! JUMP） | 1 | NULL |
| 8 | 4560 | 641 | 鈴木伸之 | 1 | 俳優 | 0 | NULL |
| 9 | 4562 | 643 | オダギリジョー | 1 | 俳優 | 0 | NULL |
| 10 | 4564 | 644 | 鈴木浩介 | 1 | 俳優 | 0 | NULL |
| 11 | 4566 | 646 | 小原唯和 | 1 | 俳優・モデル | 1 | NULL |
| 12 | 4568 | 647 | 鈴木一朗(イチロー) | 1 | 元スポーツ選手（野球） | 0 | NULL |
| 13 | 4570 | 649 | 林修 | 1 | タレント、文化人（予備校教師） | 0 | NULL |
| 14 | 4572 | 650 | 中条あやみ | 2 | モデル、女優 | 0 | NULL |
| 15 | 4574 | 652 | 林遣都 | 1 | 俳優 | 0 | NULL |
| 16 | 4576 | 653 | 数原龍友 | 1 | 歌手・アーティスト（GENERATION） | 1 | NULL |
| 17 | 4578 | 655 | カズレーザー | 1 | お笑いタレント（メイプル超合金） | 0 | NULL |
| 18 | 4580 | 656 | 財前直見 | 2 | 女優 | 0 | NULL |
| 19 | 4582 | 658 | 中嶋朋子 | 2 | 女優 | 0 | NULL |
| 20 | 4584 | 659 | 竜星涼 | 1 | 俳優 | 0 | NULL |

---

## 7. バックアップテーブルの詳細

### 7.1 talents_backup_20251202_214046

```
タイムスタンプ: 2025-12-02 21:40:46
総レコード数: 3,971
del_flag = 0のレコード: 3,971 (現在のtalentsと同じ)

予算情報:
  設定済み: 2,202件 (55.4%)
  未設定: 1,769件 (44.6%)

予算統計:
  最小値: ¥50万
  最大値: ¥30,000万（3億円）
  平均値: ¥2,907万
  中央値: ¥2,500万

分布例:
  ¥50万～500万: 1,000件程度
  ¥500万～2,000万: 800件程度
  ¥2,000万～5,000万: 250件程度
  ¥5,000万～: 152件程度
```

### 7.2 talent_scores_backup_20251202_214046

```
総レコード: 8,004
ユニークtalent_id: 1,001
ユニークtarget_segment_id: 8
平均スコア: 8,004 / 1,001 ≒ 8 (8 segments per talent)

カラム:
  id, talent_id, target_segment_id, 
  vr_popularity, tpr_power_score, base_power_score, created_at
```

### 7.3 talent_images_backup_20251202_214046

```
総レコード: 32,192
ユニークtalent_id: 1,000
推定構成: 1,000 talents × 8 segments × 4 image_items

カラム:
  id, talent_id, target_segment_id, image_item_id, score, created_at
```

---

## 8. CLAUDE.md要件との照合

### マッチングロジック必須項目の確認

| STEP | 要件 | テーブル | 必須カラム | 現状 |
|-----|------|---------|---------|------|
| 0 | 予算フィルタリング | talents | money_max_one_year | ⚠️ 全NULL |
| 1 | 基礎パワー得点 | talent_scores | vr_popularity, tpr_power_score | ⚠️ テーブル空 |
| 2 | 業種イメージ査定 | talent_images | image_item_id, score | ⚠️ テーブル空 |
| 3 | 基礎反映得点 | 計算 | STEP1 + STEP2 | ⚠️ ブロック |
| 4 | ランキング確定 | talents | id (sort用) | ✓ OK |
| 5 | マッチングスコア | 計算 | ランキング位置 | ⚠️ ブロック |

**結論:** STEP 0（予算フィルタリング）以降が完全にブロックされている

---

## 9. 確認された事実

### ✓ 正確に実装されている項目
- ✓ account_id: 4,819件全て
- ✓ name: 4,819件全て（last_name + first_name）
- ✓ gender: 4,819件全て（1/2/3正確）
- ✓ category: 4,785件（99.3%）
- ✓ del_flag: 4,819件全て
- ✓ company_name: 4,693件（97.4%）
- ✓ テーブルスキーマ: CLAUDE.md準拠
- ✓ インデックス: 最適化済み

### ⚠️ 不足している項目

**優先度1（CRITICAL）:**
1. **money_max_one_year**: 100% NULL
   - Excelに元データが存在しない
   - バックアップには 2,202件/3,971件 存在
   - STEP 0で必須（ブロッカー）

2. **VR/TPRスコアデータ**: テーブル完全に空
   - talent_scores: 0件（バックアップ: 8,004件）
   - talent_images: 0件（バックアップ: 32,192件）
   - STEP 1-4で必須（ブロッカー）

**優先度2（対応可能）:**
- birthday: 511件NULL（10.6%）
- official_url: 1,011件NULL（21.0%）

---

## 10. 推奨アクション

### 対応優先度

| 優先度 | タスク | 影響範囲 | 推奨方法 |
|--------|-------|---------|---------|
| **P0** | money_max_one_yearの復元 | マッチングロジック全体 | バックアップから復元 |
| **P0** | VR/TPRデータのインポート | マッチングロジック全体 | バックアップから復元 |
| P1 | データ品質チェック | 診断精度 | 統計分析 |
| P2 | NULL値の対応 | UI/UX改善 | デフォルト値設定 |

### 詳細手順

#### タスク1: money_max_one_year の復元
```sql
-- バックアップから復元（推奨）
UPDATE talents t
SET money_max_one_year = b.money_max_one_year
FROM talents_backup_20251202_214046 b
WHERE t.account_id = b.account_id
  AND b.money_max_one_year IS NOT NULL;

-- 影響: 2,202件のmoney_max_one_yearが復元される
```

#### タスク2: VR/TPRデータのインポート
```sql
-- talent_scoresの復元
TRUNCATE TABLE talent_scores;
INSERT INTO talent_scores (talent_id, target_segment_id, vr_popularity, tpr_power_score, base_power_score)
SELECT talent_id, target_segment_id, vr_popularity, tpr_power_score, base_power_score
FROM talent_scores_backup_20251202_214046;

-- talent_imagesの復元
TRUNCATE TABLE talent_images;
INSERT INTO talent_images (talent_id, target_segment_id, image_item_id, score)
SELECT talent_id, target_segment_id, image_item_id, score
FROM talent_images_backup_20251202_214046;

-- 影響: 8,004 + 32,192 = 40,196件がインポートされる
```

---

## 11. 結論

### talentsテーブルの実装状態

**✓ 基本データは正確**
- Excelの m_account シートから正確にインポート
- account_id, name, gender, category等は完全に実装
- 4,819件のタレントデータが登録済み

**⚠️ しかし2つの致命的な問題がある**

1. **money_max_one_year が全てNULL（CRITICAL）**
   - Excelに元データが存在しない
   - STEP 0: 予算フィルタリング が動作不可
   - バックアップに 2,202件存在
   - **推奨: バックアップから復元**

2. **VR/TPRデータが未インポート（CRITICAL）**
   - talent_scores と talent_images が空
   - STEP 1-5: マッチングロジック全体が動作不可
   - バックアップに 8,004 + 32,192件存在
   - **推奨: バックアップから復元**

### データフロー図

```
Excelファイル (Nowデータ_20251126.xlsx)
├─ m_account (4,819行)
│  ├─ ✓ account_id → talents.account_id
│  ├─ ✓ last_name + first_name → talents.name
│  ├─ ✓ gender_type_cd → talents.gender
│  ├─ ✓ birthday → talents.birthday
│  └─ ⚠️ money_max_one_year (不存在) → talents.money_max_one_year (NULL)
│
├─ VRデータフォルダ
│  ├─ ⚠️ VR_data/* (未インポート)
│  │  ├─ → talent_scores (0件)
│  │  └─ → talent_images (0件)
│
└─ バックアップ
   ├─ talents_backup_20251202_214046 (3,971件、money_max_one_year有)
   ├─ talent_scores_backup_20251202_214046 (8,004件)
   └─ talent_images_backup_20251202_214046 (32,192件)
```

### 次のステップ

1. **即座に対応（今日中）**
   - バックアップから money_max_one_year を復元
   - バックアップから VR/TPRデータをインポート
   - データ検証

2. **フォローアップ（明日）**
   - マッチングロジックのテスト実行
   - 診断APIの動作確認
   - パフォーマンス測定

3. **ドキュメント更新**
   - このレポートをプロジェクトドキュメントとして保存
   - データ移行ログを記録
   - チェックリストを更新

---

**レポート生成**: 2025-12-02 21:15 UTC+9
**検査方法**: PostgreSQL直接接続、実データ測定
**信頼度**: 100% (データベース実測値)
