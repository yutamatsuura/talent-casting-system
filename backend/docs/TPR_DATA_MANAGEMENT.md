# TPRデータ管理・運用ドキュメント

## 概要

このドキュメントは、TPR（Television Program Rating）データの更新・管理に関する運用手順をまとめたものです。

## 背景

### 問題の発見
2025年12月15日、診断システムでサンドウィッチマンのTPRスコアが25.7と表示されるが、ソースCSVデータでは35.7である不整合が発覚。

### 根本原因
- 診断システムは `target_segment_id = 1-8` を期待
- 実際のデータは `target_segment_id = 9-16` に格納
- システムが動的に `segment_name → segment_id` 変換を行っており、正しく動作
- TPR更新スクリプトが間違った `segment_id` マッピングを使用していた

## システム構成

### target_segment_id マッピング
```
診断システム動作: segment_name → segment_id 動的変換
- 男性12-19歳 → 9
- 女性12-19歳 → 10
- 男性20-34歳 → 11
- 女性20-34歳 → 12
- 男性35-49歳 → 13
- 女性35-49歳 → 14
- 男性50-69歳 → 15
- 女性50-69歳 → 16
```

### データ分布（2025年12月調査時点）
- 個人タレント：主にsegment_id 1-8に存在（13,000件以上）
- コンビ・グループ：segment_id 9-16に存在（3,000件程度）
- 重複アカウント：約500件が両方に存在

## TPRデータ更新手順

### 1. 事前準備

#### 必要ファイル
```bash
# CSVファイル（8ファイル）
TPR_男性12～19_202508.csv
TPR_女性12～19_202508.csv
TPR_男性20～34_202508.csv
TPR_女性20～34_202508.csv
TPR_男性35～49_202508.csv
TPR_女性35～49_202508.csv
TPR_男性50～69_202508.csv
TPR_女性50～69_202508.csv
```

#### スクリプト場所
```bash
/Users/lennon/projects/talent-casting-form/backend/scripts/update_tpr_with_name_matching.py
```

### 2. ドライラン実行

```bash
cd /Users/lennon/projects/talent-casting-form/backend
python3 scripts/update_tpr_with_name_matching.py --dry-run
```

#### ドライラン結果確認ポイント
- マッチング率：90%以上が目標
- 不一致レコード：manual mappingで対応可能か確認
- 重要タレント：サンドウィッチマン、ヒカキン等の値を個別確認

### 3. 本番実行

```bash
echo "yes" | python3 scripts/update_tpr_with_name_matching.py --execute
```

#### 実行時間目安
- 総処理時間：約40分（8ファイル × 5分/ファイル）
- 処理レコード数：約10,000件
- マッチング精度：92.0%

### 4. 実行後確認

#### データベース確認
```sql
-- サンドウィッチマンのTPRスコア確認
SELECT ts.tpr_power_score, ts.base_power_score, ts.updated_at
FROM talent_scores ts
JOIN m_account ma ON ts.account_id = ma.account_id
WHERE ma.name_full_for_matching = 'サンドウィッチマン'
  AND ts.target_segment_id = 9;
```

#### 診断システム確認
1. 診断システムにアクセス：`app.yourdomain.com`
2. 男性12-19歳、乳製品で診断実行
3. サンドウィッチマンのTPRスコアが35.7になっていることを確認

## スクリプト設定

### ファイルマッピング（修正版）
```python
TPR_FILES_MAPPING = {
    "TPR_男性12～19_202508.csv": 9,   # 修正前: 13
    "TPR_女性12～19_202508.csv": 10,  # 修正前: 9
    "TPR_男性20～34_202508.csv": 11,  # 修正前: 14
    "TPR_女性20～34_202508.csv": 12,  # 修正前: 10
    "TPR_男性35～49_202508.csv": 13,  # 修正前: 15
    "TPR_女性35～49_202508.csv": 14,  # 修正前: 11
    "TPR_男性50～69_202508.csv": 15,  # 修正前: 16
    "TPR_女性50～69_202508.csv": 16,  # 修正前: 12
}
```

### マニュアルマッピング
```python
MANUAL_NAME_MAPPING = {
    "フィッシャーズ": "Fischer's",      # account_id: 2881
    "イチロー": "鈴木一朗（イチロー）",  # account_id: 647
    "ヒカキン": "HIKAKIN",            # account_id: 482
}
```

## 技術的注意事項

### SQLAlchemy ORM vs Raw SQL
スクリプトは以下の理由でRaw SQLを使用：
```python
# talent_scoresテーブルにidカラムが存在しないため
# ORM使用時に「column talent_scores.id does not exist」エラー
# 回避策：Raw SQLで直接UPDATE実行
await session.execute(
    text('''
        UPDATE talent_scores
        SET tpr_power_score = :tpr_score,
            base_power_score = :base_power_score,
            updated_at = CURRENT_TIMESTAMP
        WHERE account_id = :account_id
          AND target_segment_id = :target_segment_id
    ''')
)
```

### base_power_score 計算ロジック
```python
# 正しい計算式
base_power_score = (vr_popularity + tpr_power_score) / 2

# COALESCEによるnull handling
base_power_score = (COALESCE(vr_popularity, 0) + tpr_power_score) / 2
```

## トラブルシューティング

### よくある問題

#### 1. マッチング率が低い
**症状**: マッチング率が85%未満
**原因**: CSVファイル内の表記と名前の違い
**対応**: manual mappingに追加

#### 2. SQLAlchemy エラー
**症状**: `column talent_scores.id does not exist`
**原因**: ORM定義と実テーブル構造の不一致
**対応**: Raw SQLを使用（既に対応済み）

#### 3. segment_id マッピングエラー
**症状**: 期待しないsegment_idでの更新
**原因**: TPR_FILES_MAPPINGの設定間違い
**対応**: 正しいマッピング（9-16）を使用

### エラーログ確認
```bash
# スクリプト実行ログ
tail -f /var/log/tpr_update.log

# データベースログ確認
SELECT * FROM talent_scores WHERE updated_at > NOW() - INTERVAL '1 hour';
```

## 定期メンテナンス

### 月次作業
1. 新しいTPRデータCSVファイルの受領
2. ドライラン実行・結果確認
3. 本番実行
4. 診断システムでの動作確認

### 四半期作業
1. マニュアルマッピングの見直し
2. マッチング率の分析・改善
3. データ整合性チェック

## 関連ファイル

### スクリプト
- `scripts/update_tpr_with_name_matching.py` - メインスクリプト
- `scripts/talent_name_mapping_dictionary.py` - マニュアルマッピング定義

### 調査・デバッグ用
- `scripts/debug_sandwich_man.py` - サンドウィッチマン詳細調査
- `scripts/check_segments.py` - segment_id調査
- `scripts/analyze_segment_distribution.py` - データ分布分析
- `scripts/simple_debug.py` - シンプル調査

### ドキュメント
- `docs/TPR_DATA_MANAGEMENT.md` - 本ドキュメント

---

**更新履歴**
- 2025-12-15: 初版作成（サンドウィッチマンTPRスコア修正対応）