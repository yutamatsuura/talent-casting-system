-- 診断結果保存テーブル作成
-- フォーム送信と診断結果を紐付けて、管理者が30名のタレントを確認できるようにする

CREATE TABLE diagnosis_results (
    id SERIAL PRIMARY KEY,
    form_submission_id INTEGER NOT NULL REFERENCES form_submissions(id),
    ranking INTEGER NOT NULL,
    talent_account_id INTEGER NOT NULL,
    talent_name VARCHAR(255) NOT NULL,
    talent_category VARCHAR(255),
    matching_score DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- インデックス作成（パフォーマンス向上）
CREATE INDEX idx_diagnosis_results_submission_id ON diagnosis_results(form_submission_id);
CREATE INDEX idx_diagnosis_results_ranking ON diagnosis_results(form_submission_id, ranking);

-- コメント追加
COMMENT ON TABLE diagnosis_results IS '診断結果タレント30名保存テーブル';
COMMENT ON COLUMN diagnosis_results.form_submission_id IS 'フォーム送信IDとの紐付け';
COMMENT ON COLUMN diagnosis_results.ranking IS '診断結果順位（1-30位）';
COMMENT ON COLUMN diagnosis_results.talent_account_id IS 'タレントアカウントID';
COMMENT ON COLUMN diagnosis_results.talent_name IS 'タレント名';
COMMENT ON COLUMN diagnosis_results.talent_category IS 'タレントカテゴリ（女優、アイドル等）';
COMMENT ON COLUMN diagnosis_results.matching_score IS 'マッチングスコア（86.0-99.7点）';