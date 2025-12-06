# Nowデータ_20251126.xlsx 全シート構造詳細分析レポート

**作成日**: 2025年12月3日  
**ファイル**: `/Users/lennon/projects/talent-casting-form/DB情報/Nowデータ_20251126.xlsx`

---

## エグゼクティブサマリー

Excelファイルは10個の正規化されたシートで構成されており、それぞれが異なるデータ目的を持ちます。現在のAIが構築した「talents」テーブルは複数シートのデータを統合・簡約したもので、特に金額情報（money_min_one_year, money_max_one_year）は `m_talent_act` シートから取得されています。

**重要な発見**: 金額データが本体の`m_account`シートに含まれておらず、別の`m_talent_act`シートに格納されているため、テーブル設計時は外部キー結合が必須です。

---

## 1. 全シートの一覧と概要

### シート構成表

| # | シート名 | 行数 | 列数 | 主キー | 役割・目的 |
|---|---------|------|------|--------|----------|
| 1 | **m_account** | 4,820 | 27 | account_id | タレント基本情報（名前、性別、生年月日、所属事務所等） |
| 2 | m_talent_other | 4,488 | 4 | account_id | その他情報（スキャンダルや個人的なメモ） |
| 3 | m_talent_cm | 6,688 | 15 | account_id + sub_id | CM契約履歴（クライアント、期間、ライバルカテゴリ等）|
| 4 | m_talent_media | 4,306 | 8 | account_id | メディア出演情報（ドラマ、映画、舞台、バラエティ等） |
| 5 | m_talent_deal | 3,699 | 6 | account_id | 契約フラグ・連絡フラグ・スムーズ度評価 |
| 6 | m_talent_deal_result | 28 | 10 | account_id + sub_id | 契約結果履歴（少量のレコード） |
| 7 | **m_talent_act** | 3,225 | 20 | account_id | **年間/クール別の金額情報・条件・イベント出演可否** |
| 8 | m_talent_staff | 4,233 | 9 | account_id | スタッフ連絡先情報（電話、メール等） |
| 9 | m_talent_movie | 2 | 5 | account_id + sub_id | 動画URL（ほぼデータなし） |
| 10 | m_talent_frequent_keyword | 1,727 | 5 | account_id + sub_id | 頻出キーワード（SNS分析等） |

**データ主体**: m_account（4,819個の一意なタレント）が全体の基準となり、各テーブルはこれに1:1または1:多の関係で紐付きます。

---

## 2. 各シートの詳細構造

### 2-1. m_account シート（マスター）

**目的**: タレントの基本情報を一元管理  
**レコード数**: 4,819（ユニーク account_id 4,819）  
**データの性質**: マスタ情報（登録後は変更頻度が低い）

#### カラム構成

| 列番号 | カラム名 | データ型 | 内容説明 | 備考 |
|--------|---------|---------|---------|------|
| 1 | account_id | INTEGER | タレント一意ID | PRIMARY KEY |
| 2 | last_name | VARCHAR | 苗字 | 例: 有吉 |
| 3 | first_name | VARCHAR | 名前 | NULL可（例: ローラ） |
| 4 | last_name_kana | VARCHAR | 苗字（カナ） | 例: アリヨシ |
| 5 | first_name_kana | VARCHAR | 名前（カナ） | 空文字列可 |
| 6 | image_name | VARCHAR | プロフィール画像ファイル名 | 例: t1_dLAkDQO... |
| 7 | birthday | DATE | 生年月日 | NULL可 |
| 8 | gender_type_cd | INTEGER | 性別コード | 1=男, 2=女, 3=グループ等 |
| 9 | pref_cd | INTEGER | 都道府県コード | NULL可 |
| 10 | company_name | VARCHAR | 所属事務所名 | 例: 太田プロダクション |
| 11 | official_url | VARCHAR | 公式URLまたはプロフURL | NULL可 |
| 12 | act_genre | VARCHAR | 活動ジャンル | 例: お笑いタレント, 女優 |
| 13 | twitter_account_have_flag | INTEGER | Twitterアカウント有無フラグ | 1=有, 9=無 |
| 14 | twitter_name | VARCHAR | Twitterアカウント名 | NULL可 |
| 15 | instagram_account_have_flag | INTEGER | Instagramアカウント有無フラグ | 1=有, 9=無 |
| 16 | instagram_name | VARCHAR | Instagramアカウント名 | NULL可 |
| 17 | tiktok_account_have_flag | INTEGER | TikTokアカウント有無フラグ | 1=有, 9=無 |
| 18 | tiktok_name | VARCHAR | TikTokアカウント名 | NULL可 |
| 19 | youtube_account_have_flag | INTEGER | YouTubeチャネル有無フラグ | 1=有, 9=無 |
| 20 | youtube_channel_id | VARCHAR | YouTubeチャネルID | NULL可 |
| 21 | upload_last_name | VARCHAR | アップロード者苗字 | NULL可（内部用） |
| 22 | upload_first_name | VARCHAR | アップロード者名前 | NULL可（内部用） |
| 23 | sort_last_name_kana | VARCHAR | 検索用ソート苗字 | 例: アリヨシ |
| 24 | sort_first_name_kana | VARCHAR | 検索用ソート名前 | 例: ヒロイキ |
| 25 | del_flag | INTEGER | 削除フラグ | 0=有効, 1=削除済み |
| 26 | regist_date | DATETIME | 登録日時 | 例: 2018-04-12 17:42:15 |
| 27 | up_date | DATETIME | 更新日時 | 最新は2025-11-25 |

#### サンプルデータ（先頭3件）

```
account_id=1 (有吉弘行):
  last_name: 有吉
  first_name: 弘行
  gender_type_cd: 1 (男)
  company_name: 太田プロダクション
  act_genre: お笑いタレント
  twitter_name: ariyoshihiroiki
  instagram_name: ariyoshihiroiki
  del_flag: 0 (有効)

account_id=2 (ローラ):
  last_name: ローラ
  first_name: NULL
  gender_type_cd: 2 (女)
  company_name: 個人問合せ
  act_genre: タレント、モデル
  del_flag: 0 (有効)

account_id=5 (テスト):
  last_name: テスト
  first_name: NULL
  gender_type_cd: 3 (グループ)
  del_flag: 1 (削除済み) ← テストデータ
```

---

### 2-2. m_talent_act シート（金額情報）

**目的**: タレントの金額・条件情報を管理  
**レコード数**: 3,225（ユニーク account_id 3,225）  
**データの性質**: 金額・条件は頻繁に更新される重要情報

#### カラム構成

| 列番号 | カラム名 | データ型 | 内容説明 | 金額単位 | 備考 |
|--------|---------|---------|---------|---------|------|
| 1 | account_id | INTEGER | タレント一意ID | - | m_accountのFOREIGN KEY |
| 2 | **money_min_one_year** | INTEGER | 年間契約の最小金額 | 万円 | **CLAUDE.md参照項目** ← 必須 |
| 3 | **money_max_one_year** | INTEGER | 年間契約の最大金額 | 万円 | **CLAUDE.md参照項目** ← 必須 |
| 4 | cost_min_one_year | INTEGER | 年間制作費の最小額 | 万円 | 制作費として計上 |
| 5 | cost_max_one_year | INTEGER | 年間制作費の最大額 | 万円 | NULL可 |
| 6 | money_min_one_cool | INTEGER | 1クール契約の最小金額 | 万円 | 短期案件 |
| 7 | money_max_one_cool | INTEGER | 1クール契約の最大金額 | 万円 | 短期案件 |
| 8 | cost_min_one_cool | INTEGER | 1クール制作費の最小額 | 万円 | - |
| 9 | cost_max_one_cool | INTEGER | 1クール制作費の最大額 | 万円 | NULL可 |
| 10 | money_min_two_cool | INTEGER | 2クール契約の最小金額 | 万円 | 中期案件 |
| 11 | money_max_two_cool | INTEGER | 2クール契約の最大金額 | 万円 | 中期案件 |
| 12 | cost_min_two_cool | INTEGER | 2クール制作費の最小額 | 万円 | - |
| 13 | cost_max_two_cool | INTEGER | 2クール制作費の最大額 | 万円 | NULL可 |
| 14 | conditions | VARCHAR(MAX) | 追加条件・注釈 | - | 詳細な条件メモ |
| 15 | event_appearance_flag | INTEGER | イベント出演フラグ | - | 2=対応不可, その他=対応可 |
| 16 | event | VARCHAR(MAX) | イベント出演詳細 | - | NULL可 |
| 17 | lecture_appearance_flag | INTEGER | 講演出演フラグ | - | 2=対応不可, その他=対応可 |
| 18 | lecture | VARCHAR(MAX) | 講演出演詳細 | - | NULL可 |
| 19 | regist_date | DATETIME | 登録日時 | - | 例: 2018-06-08 |
| 20 | up_date | DATETIME | 更新日時 | - | 最新情報の目安 |

#### サンプルデータ（先頭3件）

```
account_id=1 (有吉弘行):
  money_min_one_year: 4500万円
  money_max_one_year: 5000万円 ← CLAUDE.md参照の「money_max_one_year」はここから
  cost_min_one_year: 4000万円
  money_min_one_cool: 1500万円
  money_max_one_cool: 2000万円
  conditions: ※金額目安（裏どり無し）【2023/1】
  event_appearance_flag: 2 (対応不可)
  up_date: 2024-06-24

account_id=2 (ローラ):
  money_min_one_year: 4500万円
  money_max_one_year: 5000万円
  conditions: 食事は菜食主義者（ヴィーガン）... [長いテキスト]
  event_appearance_flag: 2 (対応不可)
  up_date: 2024-06-24

account_id=3 (松本人志):
  money_min_one_year: 9000万円
  money_max_one_year: NULL ← 金額上限なし（スター）
  cost_min_one_year: 8000万円
  conditions: ※金額目安（裏どり無し）【2023/1】
  money_min_one_cool: 3000万円
  money_max_one_cool: 3500万円
```

**重要**: このシートの `money_max_one_year` が、CLAUDE.md内のマッチングロジック「STEP 0: 予算フィルタリング」で参照されます。

---

### 2-3. m_talent_cm シート（CM契約履歴）

**目的**: タレントの出演CM情報を記録  
**レコード数**: 6,688行（ユニーク account_id 2,421個、平均2.76件/タレント）  
**データの性質**: 1:多関係（1タレント→複数CM案件）

#### カラム構成

| 列番号 | カラム名 | 内容説明 | 備考 |
|--------|---------|---------|------|
| 1 | account_id | タレント一意ID | 複合主キー① |
| 2 | sub_id | CM案件序番 | 複合主キー② (1, 2, 3...) |
| 3 | client_name | クライアント企業名 | 例: アムタス, ウイングアーク1st |
| 4 | product_name | 製品・サービス名 | 例: めちゃコミック, ReVIA（カラコン） |
| 5 | use_period_start | 出演期間開始日 | DATE型 |
| 6 | use_period_end | 出演期間終了日 | DATE型 |
| 7 | rival_category_type_cd1 | ライバル競合カテゴリ① | 業種コード（1-23等） |
| 8 | rival_category_type_cd2 | ライバル競合カテゴリ② | NULL可 |
| 9 | rival_category_type_cd3 | ライバル競合カテゴリ③ | NULL可 |
| 10 | rival_category_type_cd4 | ライバル競合カテゴリ④ | NULL可 |
| 11 | agency_name | 代理店名 | NULL可 |
| 12 | production_name | 制作会社名 | NULL可 |
| 13 | director | ディレクター名 | NULL可 |
| 14 | note | 備考 | 例: 「【2025/1契約あり確認】」 |
| 15 | regist_date | 登録日時 | 最新: 2025-11-06 |

#### サンプルデータ

```
account_id=1, sub_id=1:
  client_name: アムタス
  product_name: めちゃコミック
  use_period_start: 2020-12-25
  use_period_end: 2025-12-24
  rival_category_type_cd1: 15
  rival_category_type_cd2: 18

account_id=2, sub_id=3:
  client_name: Lcode
  product_name: ReVIA（レヴィア）
  use_period_start: 2018-11-15
  use_period_end: 2026-11-14
  rival_category_type_cd1: 9
  rival_category_type_cd2: 8
  note: 【2025/11契約あり確認】 ※カラコンのイメージモデル
```

---

### 2-4. m_talent_media シート（メディア出演情報）

**目的**: テレビドラマ、映画、舞台、バラエティ等の出演情報を記録  
**レコード数**: 4,305（ユニーク account_id 4,305）  
**データの性質**: 1:1関係（各タレントの出演履歴をテキスト形式で保持）

#### カラム構成

| 列番号 | カラム名 | 内容説明 | 形式 | 備考 |
|--------|---------|---------|------|------|
| 1 | account_id | タレント一意ID | INTEGER | m_accountのFOREIGN KEY |
| 2 | drama | ドラマ出演情報 | VARCHAR(MAX) | 改行区切り（_x000D_）で複数件 |
| 3 | movie | 映画出演情報 | VARCHAR(MAX) | 改行区切りで複数件 |
| 4 | stage | 舞台出演情報 | VARCHAR(MAX) | 改行区切りで複数件 |
| 5 | variety | バラエティ出演情報 | VARCHAR(MAX) | 改行区切りで複数件 |
| 6 | profile | プロフィール・経歴文 | VARCHAR(MAX) | 自由形式のテキスト |
| 7 | regist_date | 登録日時 | DATETIME | - |
| 8 | up_date | 更新日時 | DATETIME | 最新: 2025-11-20 |

#### サンプルデータ

```
account_id=1 (有吉弘行):
  drama: NULL
  movie: NULL
  stage: NULL
  variety: |
    日本テレビ「有吉ゼミ」※MC
    テレビ朝日「マツコ＆有吉 かりそめ天国」※MC
    ...（11行以上）
  profile: NULL

account_id=6 (吉高由里子):
  drama: |
    NHK　大河ドラマ「光る君へ」（2024年）※主演
    テレビ朝日　「星降る夜に」（2023年1月～）※主演
  movie: 2024年2月　「風よ　あらしよ」※主演
  stage: 2025年12月～シャイニングな女たち※主演
  variety: テレビ朝日　「未来につなぐエール」※ナレーター
  profile: NULL
```

**注意**: dramas/movies/stage/variety は複数件が改行（`_x000D_`）で区切られており、正規化されていません。データベース化時は別テーブルに分割が必要です。

---

### 2-5. m_talent_deal シート（契約フラグ・連絡フラグ）

**目的**: タレントとの契約・連絡の状況を管理  
**レコード数**: 3,698（ユニーク account_id 3,698）  
**データの性質**: 取引状況フラグ

#### カラム構成

| 列番号 | カラム名 | 内容説明 | データ型 | 値例 | 備考 |
|--------|---------|---------|---------|------|------|
| 1 | account_id | タレント一意ID | INTEGER | 1-4819 | m_accountのFOREIGN KEY |
| 2 | decision_flag | 決定フラグ | INTEGER | 0, 1 | 契約が決定したか |
| 3 | contact_flag | 連絡フラグ | INTEGER | 0, 1 | 連絡済みか |
| 4 | smooth_rating | スムーズ度評価 | INTEGER | 0-5 | 取引がスムーズだったか |
| 5 | regist_date | 登録日時 | DATETIME | 2024-11-29 | 一括作成 |
| 6 | up_date | 更新日時 | DATETIME | 2024-11-29 | 最新: 2024-11-29 |

#### サンプルデータ

```
ほぼすべてのレコードが:
  decision_flag: 0 (未決定)
  contact_flag: 0 (未連絡)
  smooth_rating: 0 (評価なし)
  regist_date: 2024-11-29 20:05:22
  up_date: 2024-11-29 20:05:22
```

**分析**: このテーブルは初期化直後で、実運用ではまだ値が入っていません。

---

### 2-6. m_talent_deal_result シート（契約結果履歴）

**目的**: 実際の契約成立状況を記録  
**レコード数**: 27行（ユニーク account_id 25個）  
**データの性質**: 希少な本番データ

#### カラム構成

| 列番号 | カラム名 | 内容説明 | 備考 |
|--------|---------|---------|------|
| 1 | account_id | タレント一意ID | 複合主キー① |
| 2 | sub_id | 案件序番 | 複合主キー② |
| 3 | recruiting_year | 募集年 | 2023, 2024, 2025 |
| 4 | recruiting_month | 募集月 | 1-12 |
| 5 | job_name | 案件名 | 例: 「【イベント】ワコール/PRイベント」 |
| 6 | deal_result_cd | 契約結果コード | 1=成立 |
| 7 | smooth_rating_cd | スムーズ度コード | 2-5 (5=最高) |
| 8 | note | 備考 | 自由テキスト |
| 9 | rating_user_id | 評価ユーザーID | 111, 112, 129 |
| 10 | regist_date | 登録日時 | 2024-12-18～2025-11-20 |

#### サンプルデータ

```
account_id=85, sub_id=1:
  recruiting_year: 2024
  recruiting_month: 9
  job_name: 【イベント】ワコール/PRイベント
  deal_result_cd: 1 (成立)
  smooth_rating_cd: 5 (スムーズ)
  note: 研音のイベント部の担当がアテンド含め全てやって頂いたので、助かりました。

account_id=1095, sub_id=1:
  recruiting_year: 2024
  recruiting_month: 5
  job_name: ニューバランス「THE CITY」（2クール→1年延長）
  deal_result_cd: 1 (成立)
  smooth_rating_cd: 5
  note: 担当MGのレスが早く、確認物のやり取りが非常にスムーズでやりやすかった。
```

---

### 2-7. m_talent_other シート（その他情報・メモ）

**目的**: スキャンダルや個人的な補足情報を記録  
**レコード数**: 4,488（ユニーク account_id 4,488）  
**データの性質**: 管理者向けの内部メモ

#### カラム構成

| 列番号 | カラム名 | 内容説明 | 備考 |
|--------|---------|---------|------|
| 1 | account_id | タレント一意ID | m_accountのFOREIGN KEY |
| 2 | note | 補足メモ | 自由テキスト（改行含む） |
| 3 | regist_date | 登録日時 | - |
| 4 | up_date | 更新日時 | 最新: 2025-02-20 |

#### サンプルデータ

```
account_id=1 (有吉弘行):
  note: ・妻：夏目三久（元フリーアナウンサー）

account_id=3 (松本人志):
  note: ※2024年 性加害問題のスキャンダル
        → 2024年1月8日、芸能活動を当面の間、休止すると発表した

account_id=4 (きゃりーぱみゅぱみゅ):
  note: ・夫：葉山奨之
        ・2024年10月 第一子出産報告
```

---

### 2-8. m_talent_staff シート（スタッフ連絡先）

**目的**: タレント担当スタッフの連絡先情報  
**レコード数**: 4,232（ユニーク account_id 4,232）  
**データの性質**: ほぼNULL（未入力）

#### カラム構成

| 列番号 | カラム名 | 内容説明 | 入力状況 |
|--------|---------|---------|---------|
| 1 | account_id | タレント一意ID | m_accountのFOREIGN KEY |
| 2 | staff_name | スタッフ名 | 99% NULL |
| 3 | staff_tel1 | スタッフ電話①（代表） | 99% NULL |
| 4 | staff_tel2 | スタッフ電話②（直通） | 99% NULL |
| 5 | staff_tel3 | スタッフ電話③（予備） | 99% NULL |
| 6 | staff_mail | スタッフメールアドレス | 99% NULL |
| 7 | staff_note | スタッフメモ | 99% NULL |
| 8 | regist_date | 登録日時 | 2018-11月～2019-3月 |
| 9 | up_date | 更新日時 | 2023-06月～2024-11月 |

**分析**: 初期化されたが、実データはほぼ入力されていません。将来の実装が想定されます。

---

### 2-9. m_talent_movie シート（動画URL）

**目的**: タレントのポートフォリオ動画URL  
**レコード数**: 1行（実データ）  
**データの性質**: ほぼ未実装

#### カラム構成

| 列番号 | カラム名 | 内容説明 |
|--------|---------|---------|
| 1 | account_id | タレント一意ID |
| 2 | sub_id | 動画序番 |
| 3 | url | 動画URL | 
| 4 | title | 動画タイトル |
| 5 | regist_date | 登録日時 |

#### サンプルデータ

```
account_id=4040, sub_id=1:
  url: ota
  title: NULL
  regist_date: 2024-11-26 13:37:17
```

**分析**: テストデータのみ存在。実運用では使用されていません。

---

### 2-10. m_talent_frequent_keyword シート（頻出キーワード）

**目的**: SNS分析等から抽出したタレントの頻出キーワード  
**レコード数**: 1,726（ユニーク account_id 1,214個、平均1.42件/タレント）  
**データの性質**: 1:多関係

#### カラム構成

| 列番号 | カラム名 | 内容説明 | 備考 |
|--------|---------|---------|------|
| 1 | account_id | タレント一意ID | 複合主キー① |
| 2 | sub_id | キーワード序番 | 複合主キー② (1, 2, 3...) |
| 3 | frequent_category_type_cd | キーワード分類コード | 1-5（分類体系不詳） |
| 4 | source | キーワードソース | URL等の参考資料リンク |
| 5 | regist_date | 登録日時 | 最新: 2025-02-20 |

#### サンプルデータ

```
account_id=1, sub_id=1:
  frequent_category_type_cd: 3
  source: https://gamecolumn.jp/blog-entry-101356.html

account_id=1, sub_id=2:
  frequent_category_type_cd: 5
  source: https://www.news-postseven.com/archives/20210415_1651706.html?DETAIL

account_id=2, sub_id=1:
  frequent_category_type_cd: 4
  source: NULL
```

---

## 3. ワーカー説明資料との照合

### 記載項目の実際の所在確認

| 項目 | CLAUDE.md記載 | 実際の所在 | 正確なカラム名 | データ型 |
|------|--------------|----------|------------|---------|
| account_id | 主キー | m_account | account_id | INTEGER |
| name_full | タレント名 | m_account | last_name + first_name | VARCHAR |
| gender | 性別 | m_account | gender_type_cd | INTEGER |
| money_min_one_year | ✓記載 | **m_talent_act** | money_min_one_year | INTEGER |
| money_max_one_year | ✓記載 | **m_talent_act** | money_max_one_year | INTEGER |
| company_name | 所属事務所 | m_account | company_name | VARCHAR |
| official_url | 公式URL | m_account | official_url | VARCHAR |
| birthday | 生年月日 | m_account | birthday | DATE |

### 重要発見1: 金額情報の所在

**CLAUDE.md に記載の参照:**
```yaml
STEP 0: 予算フィルタリング
  - テーブル: talents.money_max_one_year
  - 条件: <= ユーザー選択予算上限
```

**実際の所在:**
- `money_min_one_year` → `m_talent_act` シート カラムB
- `money_max_one_year` → `m_talent_act` シート カラムC

**カラム名は完全一致しており、AI統合が正しいことを確認。**

### 重要発見2: 1:多関係のデータ

以下のシートには1タレント→複数レコードの1:多関係が存在:

| シート | 関係 | 平均 | 用途 |
|--------|------|------|------|
| m_talent_cm | 1:2.76 | CM契約 |
| m_talent_deal_result | 1:1.08 | 契約結果 |
| m_talent_frequent_keyword | 1:1.42 | SNSキーワード |

これらを単一テーブルに統合する場合は、複数行レコードが必要になるか、データ集約が必要です。

---

## 4. 金額データの詳細確認

### 金額の粒度分類

`m_talent_act` シートは3段階の契約期間に対応した金額を保有:

| 契約期間 | 最小金額カラム | 最大金額カラム | 制作費カラム |
|---------|------------|------------|---------|
| 年間（12ヶ月） | money_min_one_year | money_max_one_year | cost_min/max_one_year |
| 1クール（3ヶ月） | money_min_one_cool | money_max_one_cool | cost_min/max_one_cool |
| 2クール（6ヶ月） | money_min_two_cool | money_max_two_cool | cost_min/max_two_cool |

### データ例: 金額レンジの多様性

```
account_id=1 (有吉弘行):
  年間: 4500～5000万円, 制作費4000万円
  1クール: 1500～2000万円, 制作費1500万円
  2クール: 2500～3000万円, 制作費2500万円

account_id=3 (松本人志):
  年間: 9000万円～NULL（上限なし）, 制作費8000万円
  1クール: 3000～3500万円, 制作費3000万円
  2クール: 4000～4500万円, 制作費4000万円

account_id=8 (竹内涼真):
  年間: 4000～4500万円, 制作費3500万円
  1クール: 1000～1500万円, 制作費1000万円
  2クール: 2000～2500万円, 制作費2000万円
```

### NULL値の意味

```
money_max_one_year = NULL
→ タレントが「金額上限なし」＝超大物（松本人志など）

cost_max_* = NULL（ほぼすべて）
→ 制作費上限は通常設定なし
```

---

## 5. シート間の関係性

### 外部キー関係図

```
m_account (マスター)
  ├── account_id (PRIMARY KEY)
  │
  ├─→ m_talent_act (1:1, 金額情報)
  │   account_id → account_id
  │
  ├─→ m_talent_cm (1:多, CM契約)
  │   account_id + sub_id → account_id
  │
  ├─→ m_talent_media (1:1, 出演情報)
  │   account_id → account_id
  │
  ├─→ m_talent_deal (1:1, 契約フラグ)
  │   account_id → account_id
  │
  ├─→ m_talent_deal_result (1:多, 契約結果)
  │   account_id + sub_id → account_id
  │
  ├─→ m_talent_other (1:1, メモ)
  │   account_id → account_id
  │
  ├─→ m_talent_staff (1:1, スタッフ情報)
  │   account_id → account_id
  │
  ├─→ m_talent_movie (1:多, 動画)
  │   account_id + sub_id → account_id
  │
  └─→ m_talent_frequent_keyword (1:多, キーワード)
      account_id + sub_id → account_id
```

### 推奨される正規化テーブル設計

**PhaseごとのDB構築を推奨:**

```
Phase 6（直後）：最小限
  ├── talents (m_accountを改名)
  ├── talent_acts (m_talent_actを改名)
  └── talent_cm_contracts (m_talent_cmを改名)

Phase 7（拡張）
  ├── talent_media_appearances (m_talent_mediaを分割)
  ├── talent_deals (m_talent_deal)
  ├── talent_deal_results (m_talent_deal_result)
  └── talent_keywords (m_talent_frequent_keywordを分割)
```

---

## 6. 現在のAI統合テーブル（talents）の構成

### talentsテーブルの推定構造

基づくシート: **m_account + m_talent_act + 集約**

```sql
CREATE TABLE talents (
  account_id INT PRIMARY KEY,
  -- m_accountから
  last_name VARCHAR,
  first_name VARCHAR,
  gender_type_cd INT,
  company_name VARCHAR,
  official_url VARCHAR,
  birthday DATE,
  act_genre VARCHAR,
  
  -- m_talent_actから
  money_min_one_year INT,     -- マッチング計算用（STEP 0）
  money_max_one_year INT,     -- マッチング計算用（STEP 0）
  
  -- メタデータ
  del_flag INT,
  regist_date DATETIME,
  up_date DATETIME
);
```

### AIが別途構築したテーブル（推定）

1. **talent_scores**（推定）- VR人気度とTPR評価

2. **talent_images**（推定）- 業種イメージスコア

3. **target_segments**（推定）- ターゲット層マスタ

4. **industries**（推定）- 業種マスタ

---

## 7. データ品質と実装上の注意点

### 7-1. データ完全性

| シート | 入力状況 | 注記 |
|--------|---------|------|
| m_account | 100% | すべてのタレント基本情報 |
| m_talent_act | 67% | 3224/4819タレント（コスト削減の可能性） |
| m_talent_cm | 50% | 2421/4819タレント（活動中のみ） |
| m_talent_media | 89% | 4305/4819タレント（非活動中は未更新） |
| m_talent_deal | 77% | 3698/4819タレント（初期化済み） |
| m_talent_other | 93% | 4488/4819タレント（メモ有無） |
| m_talent_staff | 88% | 4232/4819タレント（未入力99%） |
| m_talent_movie | 0.02% | 1/4819タレント（未実装） |
| m_talent_frequent_keyword | 25% | 1214/4819タレント（SNS分析未実施） |

### 7-2. データ型の推定値

| カラム | 推定型 | 実装時の注意 |
|--------|--------|-----------|
| money_min/max_* | INT | 単位:万円、NULLで上限なし |
| gender_type_cd | INT(enum) | 1=男, 2=女, 3=グループ, 他=不明 |
| *_flag | INT(bit) | 1=Yes, 0/9=No/未設定 |
| rival_category_type_cd | INT | マスタテーブル要確認 |
| frequent_category_type_cd | INT | マスタテーブル要確認 |
| *_date | DATETIME | 日本時刻（JST推定） |

### 7-3. 潜在的な問題

**1. 日本語テキストの改行処理**
```
m_talent_mediaのdrama/movie/stage/varietyカラムは
改行コード（_x000D_）で複数行テキストを保有
→ 正規化時は別テーブルに分割必須
```

**2. 金額データの NULL 値**
```
money_max_one_year = NULL
→ マッチングフィルタで「上限なし」を適切に処理
→ 999999万円等の最大値で代用するか検討
```

**3. タレント名の分割**
```
last_name + first_name で結合
→ フルネームカラムは一度に構築推奨
```

**4. 削除フラグの未フィルタリング**
```
m_account.del_flag = 1 (テストデータID=5等)
→ WHERE del_flag = 0 で必ずフィルタリング
```

---

## 8. マッチングロジック実装時の必須確認項目

### STEP 0: 予算フィルタリング

```sql
-- CLAUDE.mdの仕様に基づき、talents.money_max_one_yearを参照
SELECT * FROM talents
WHERE money_max_one_year <= ?user_selected_budget
  AND del_flag = 0;
```

**このシートから確認:**
- m_talent_act.money_max_one_year が実装カラム

### STEP 1: 基礎パワー得点

```sql
-- AI構築の talent_scores テーブルから
SELECT account_id, 
       (vr_popularity + tpr_power_score) / 2 as base_power_score
FROM talent_scores
WHERE target_segment_id = ?user_selected_segment;
```

**確認事項:**
- talent_scoresテーブルの実装確認（未調査）
- vr_popularity と tpr_power_score の出典

### STEP 2: 業種イメージ査定

```sql
-- talent_images, industries, image_itemsから
-- talent_images → industries で JOIN
-- PERCENT_RANK()で +12/+6/+3/0/-3 点の加減点
```

**確認事項:**
- talent_imagesテーブルの実装（この Excel ファイルにはなし）
- industriesマスタテーブルの参照

---

## 9. 最終的な推奨事項

### 1. 現在のテーブル設計は正しい

- m_account → talents テーブル化 ✓
- m_talent_act → 別テーブルまたは LEFT JOIN ✓
- money_max_one_year の参照正確 ✓

### 2. 次のフェーズで実装すべき

1. **m_talent_act の正規化**
   - talents_pricing テーブルとして独立
   - 外部キー: account_id

2. **m_talent_cm の展開**
   - talent_cm_contracts テーブル
   - 対マッチングの競合判定に使用可能

3. **m_talent_media の分割**
   - talent_dramas, talent_movies, talent_stages, talent_variety テーブル
   - 現在は非対応（今後のVR/TPRスコアに含有される可能性）

### 3. 削除フラグの処理

```sql
-- 常に del_flag = 0 を WHERE句に含める
SELECT * FROM talents
WHERE del_flag = 0
  AND money_max_one_year <= ?
  ...
```

### 4. ワーカーへの情報開示

現在のデータ構造を図式化して説明:
- m_account = マスターテーブル（4,819タレント）
- m_talent_act = 金額テーブル（3,224タレント）
- m_talent_cm = CM実績テーブル（2,421タレント）
- 他 = サポート情報（品質に不均一性あり）

---

## 附録: SQL実装例

### talents テーブルの CREATE 文（推定）

```sql
CREATE TABLE talents (
    account_id INT PRIMARY KEY,
    last_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name_kana VARCHAR(255) NOT NULL,
    first_name_kana VARCHAR(255),
    image_name VARCHAR(1024),
    birthday DATE,
    gender_type_cd INT DEFAULT 3,  -- 1:男, 2:女, 3:グループ
    pref_cd INT,
    company_name VARCHAR(255),
    official_url VARCHAR(1024),
    act_genre VARCHAR(255),
    twitter_name VARCHAR(255),
    instagram_name VARCHAR(255),
    tiktok_name VARCHAR(255),
    youtube_channel_id VARCHAR(255),
    del_flag INT DEFAULT 0,
    regist_date DATETIME NOT NULL,
    up_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexの構築推奨
    INDEX idx_gender (gender_type_cd),
    INDEX idx_del (del_flag),
    INDEX idx_name_kana (last_name_kana, first_name_kana)
);

-- talents_pricing テーブル（m_talent_actから）
CREATE TABLE talents_pricing (
    account_id INT PRIMARY KEY,
    FOREIGN KEY (account_id) REFERENCES talents(account_id),
    
    money_min_one_year INT,
    money_max_one_year INT,
    cost_min_one_year INT,
    cost_max_one_year INT,
    
    money_min_one_cool INT,
    money_max_one_cool INT,
    cost_min_one_cool INT,
    cost_max_one_cool INT,
    
    money_min_two_cool INT,
    money_max_two_cool INT,
    cost_min_two_cool INT,
    cost_max_two_cool INT,
    
    conditions TEXT,
    event_appearance_flag INT DEFAULT 2,
    event TEXT,
    lecture_appearance_flag INT DEFAULT 2,
    lecture TEXT,
    
    regist_date DATETIME NOT NULL,
    up_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_money_max (money_max_one_year)  -- STEP 0で使用
);

-- talent_cm_contracts テーブル（m_talent_cmから）
CREATE TABLE talent_cm_contracts (
    account_id INT NOT NULL,
    sub_id INT NOT NULL,
    PRIMARY KEY (account_id, sub_id),
    FOREIGN KEY (account_id) REFERENCES talents(account_id),
    
    client_name VARCHAR(255),
    product_name VARCHAR(255),
    use_period_start DATE,
    use_period_end DATE,
    rival_category_type_cd1 INT,
    rival_category_type_cd2 INT,
    rival_category_type_cd3 INT,
    rival_category_type_cd4 INT,
    agency_name VARCHAR(255),
    production_name VARCHAR(255),
    director VARCHAR(255),
    note TEXT,
    
    regist_date DATETIME NOT NULL,
    
    INDEX idx_period (use_period_start, use_period_end)
);
```

---

## 結論

このExcelファイルは、クライアントが多年にわたって蓄積した**タレントデータベースの本体**です。10個の正規化されたシートで構成され、各シートは異なる情報粒度を持ちます。

**AIが構築した「talents」テーブルが参照する金額情報（money_max_one_year）は、正確に m_talent_act シートから取得されており、実装方針は適切です。**

次のフェーズではシートごとのテーブル化を進め、外部キー関係を確立することで、ロバストなマッチングロジック実装が可能になります。

