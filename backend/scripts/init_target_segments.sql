-- ターゲット層マスタテーブル作成（CLAUDE.md + requirements.md準拠）
-- 作成日: 2025-11-28
-- 目的: 8ターゲット層（男性・女性 × 4年齢区分）の管理

-- テーブルが存在する場合は削除して再作成
DROP TABLE IF EXISTS target_segments CASCADE;

-- target_segments テーブル作成
CREATE TABLE target_segments (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    age_range VARCHAR(50) NOT NULL,
    display_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成（検索最適化）
CREATE INDEX idx_target_segments_code ON target_segments(code);
CREATE INDEX idx_target_segments_display_order ON target_segments(display_order);

-- 初期データ投入（8ターゲット層）
-- target_segment_id: 1-8 で VR/TPR データと紐付け
INSERT INTO target_segments (id, code, name, gender, age_range, display_order) VALUES
(1, 'M1', '男性12-19', '男性', '12-19', 1),
(2, 'F1', '女性12-19', '女性', '12-19', 2),
(3, 'M2', '男性20-34', '男性', '20-34', 3),
(4, 'F2', '女性20-34', '女性', '20-34', 4),
(5, 'M3', '男性35-49', '男性', '35-49', 5),
(6, 'F3', '女性35-49', '女性', '35-49', 6),
(7, 'M4', '男性50-69', '男性', '50-69', 7),
(8, 'F4', '女性50-69', '女性', '50-69', 8);

-- シーケンスを8にリセット（次のINSERTは9から開始）
SELECT setval('target_segments_id_seq', 8, true);

-- 確認クエリ
SELECT * FROM target_segments ORDER BY display_order;
