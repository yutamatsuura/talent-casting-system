# 🎯 完全データインポート実行計画
**作成日**: 2025年12月2日 23:30
**対象**: 全10シート・約340,000件の完全データ統合

---

## ❗ 緊急対応必須事項

### 🔧 Phase 1.1: m_accountシート完全インポート（最優先）

**問題**: m_accountシートの27項目中、大部分が未処理状態

**解決策**: talentsテーブルスキーマを確認し、全27項目を正しくマッピング

**必要作業**:
1. talentsテーブルの実際のカラム構造確認
2. m_accountシート全27項目の完全マッピング実装
3. VR照合対応の名前生成（スペースなし「有吉弘行」）確保

---

## 📋 完全インポート手順

### Phase 1: Excelデータ完全インポート（10シート）

#### 1.1 m_accountシート → talentsテーブル（4,819人・27項目）

**重要仕様**:
- last_name + first_name → name（スペースなし「有吉弘行」）
- 全27項目の完全マッピング

**Excel項目 → DBカラム マッピング**:
```
基本情報:
account_id → account_id
last_name + first_name → name (スペースなし)
last_name_kana + first_name_kana → kana
birthday → birthday, birth_year
gender_type_cd → gender
pref_cd → 都道府県コード
company_name → company_name
official_url → official_url
act_genre → category
image_name → image_name

SNS情報:
twitter_account_have_flag → twitter_有無フラグ
twitter_name → twitter_name
instagram_account_have_flag → instagram_有無フラグ
instagram_name → instagram_name
tiktok_account_have_flag → tiktok_有無フラグ
tiktok_name → tiktok_name
youtube_account_have_flag → youtube_有無フラグ
youtube_channel_id → youtube_channel_id

管理情報:
upload_last_name → upload_last_name
upload_first_name → upload_first_name
sort_last_name_kana → sort_last_name_kana
sort_first_name_kana → sort_first_name_kana
del_flag → del_flag
regist_date → regist_date
up_date → updated_at
```

#### 1.2 残り9シートのインポート

| Excelシート | DBテーブル | レコード数 | 処理内容 |
|------------|-----------|----------|----------|
| m_talent_act | talent_pricing | 3,224件 | ギャラ情報 |
| m_talent_cm | talent_cm_history | 6,687件 | CM履歴 |
| m_talent_media | talent_media_experience | 4,305件 | メディア経験 |
| m_talent_deal | talent_business_info | 3,698件 | ビジネス情報 |
| m_talent_deal_result | talent_deal_results | 27件 | 取引結果 |
| m_talent_staff | talent_contacts | 4,232件 | 連絡先 |
| m_talent_movie | talent_movies | 1件 | 動画情報 |
| m_talent_frequent_keyword | talent_keywords | 1,726件 | キーワード |
| m_talent_other | talent_notes | 4,487件 | その他情報 |

---

### Phase 2: VR/TPRデータ処理

#### 2.1 VRデータ処理（16ファイル）
**場所**: `/Users/lennon/projects/talent-casting-form/DB情報/VR_data/`
**処理内容**: 270,000件のイメージデータ → talent_imagesテーブル

#### 2.2 TPRデータ処理
**処理内容**: 38,400件のスコアデータ → talent_scoresテーブル

#### 2.3 base_power_score計算
**計算式**: (vr_popularity + tpr_power_score) / 2

---

### Phase 3: システム動作検証

#### 3.1 5段階マッチングロジックテスト
- STEP 0: 予算フィルタリング
- STEP 1-5: 完全なマッチングロジック動作確認

---

## 🛠️ 技術的重要事項

### VR照合仕様
- 名前形式: 「有吉弘行」（スペースなし）
- Unicode正規化: NFKC適用
- 異体字対応: 実装済み

### データ整合性要件
- account_id: 1-4,819の連続性
- del_flag=0: 3,971人（有効）
- del_flag=1: 848人（削除済みだが保持）

### パフォーマンス要件
- 5段階マッチング: 3秒以内
- 設計値: 242ms
- PostgreSQL PERCENT_RANK()活用

---

## ⚠️ 注意事項

### データベース接続
```
DATABASE_URL="postgresql://neondb_owner:npg_9fvZtIKj3gHe@ep-wild-art-a1dq56d3-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
```

### 実行環境
- Excel: `/Users/lennon/projects/talent-casting-form/DB情報/Nowデータ_20251126.xlsx`
- VR: `/Users/lennon/projects/talent-casting-form/DB情報/VR_data/`
- 実行計画書: `/Users/lennon/projects/talent-casting-form/docs/EXECUTION_PLAN_20251202.md`

---

## ✅ 完了確認チェックリスト

### Phase 1完了条件
- [ ] m_account: 4,819人・全27項目完全インポート
- [ ] 残り9シート: 約30,000件インポート完了
- [ ] VR照合対応名前確認（「有吉弘行」形式）

### Phase 2完了条件
- [ ] VR: 270,000件インポート完了
- [ ] TPR: 38,400件インポート完了
- [ ] base_power_score計算完了

### Phase 3完了条件
- [ ] 5段階マッチングロジック正常動作
- [ ] レスポンス時間3秒以内達成

---

## 📈 予想データ規模（最終目標）

| データ種別 | レコード数 | 現在の状況 |
|-----------|----------|-----------|
| talents | 4,819人 | ✅ 基本のみ・要完全化 |
| talent_images | 270,000件 | ❌ 未処理 |
| talent_scores | 38,400件 | ❌ 未処理 |
| その他テーブル | 約30,000件 | ❌ 未処理 |
| **合計** | **約340,000件** | **現在: 4,819件（1.4%）** |

---

**次のAIエージェントへ**: まずm_accountシートの全27項目完全インポートから開始し、段階的に全データを統合してください。