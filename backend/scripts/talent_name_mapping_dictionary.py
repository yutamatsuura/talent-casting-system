#!/usr/bin/env python3
"""
TPRインポート用タレント名前マッピング辞書
高スコア失敗ケースの手動マッピング定義
"""

# 確認済み高スコア失敗ケースの手動マッピング辞書
# CSV名 -> DB正確名の対応表
MANUAL_NAME_MAPPING = {
    # 確認済みDBマッチ（実際のaccount_id確認済み）
    "イチロー": "鈴木一朗（イチロー）",  # account_id: 647 (有効)
    "ヒカキン": "HIKAKIN",            # account_id: 482 (有効)

    # ユーザー指定account_id（効果不明だが設定）
    "B'z": "B'z",                    # account_id: 1802
    "[ALEXANDROS]": "[ALEXANDROS]",  # account_id: 2726
    "SAKURA（宮脇咲良/LE SSERAFIM）": "SAKURA（宮脇咲良/LE SSERAFIM）",  # account_id: 404
    "ØMI（登坂広臣（三代目 J SOUL BROTHERS））": "ØMI（登坂広臣（三代目 J SOUL BROTHERS））",  # account_id: 274

    # 確認済み有効なマッピング
    "フィッシャーズ": "Fischer's",      # account_id: 2881 (ユーザー確認済み)

    # 高スコア失敗ケース - DB内に存在しない可能性があるが、代替候補でマッピング
    # 注意: これらは推測マッピング - 実際のDBで確認が必要

    # 括弧除去パターン（あいまいマッチの成功パターンに基づく）
    "山添寛（相席スタート）": "山添寛",        # 括弧内グループ名を除去
    "栗谷（カカロニ）": "栗谷",                # 括弧内グループ名を除去

    # よくある表記ゆれ - カタカナ/英字変換
    "スピッツ": "SPITZ",                     # カタカナ → 英字
    "エグザイル": "EXILE",                   # 逆引き用も追加

    # アポストロフィ・記号の正規化
    "'＝LOVE": "＝LOVE",                     # 成功例パターンに基づく

    # 特殊文字の正規化
    "IS:SUE": "IS：SUE",                    # コロン → 全角コロン（成功例より）

    # よくある表記ゆれパターン（推測）
    # 注意: これらは実際のDB名前を確認して追加する必要があります

    # アーティスト・グループ名の表記ゆれ
    # "B'z": "B'z",  # アポストロフィの種類が異なる可能性
    # "スピッツ": "SPITZ",  # カタカナ vs 英字
    # "THE ALFEE": "ALFEE",  # THE の有無
    # "ケツメイシ": "ケツメイシ",  # そのまま

    # アナウンサー・タレント名
    # 実際のDB調査が必要
    # "弘中綾香": "弘中綾香",
    # "大江麻理子": "大江麻理子",
    # "田中瞳": "田中瞳",
    # "宮司愛海": "宮司愛海",

    # スポーツ選手
    # "鈴木誠也": "鈴木誠也",

    # 音楽アーティスト
    # "秦基博": "秦基博",
    # "JUJU": "JUJU",
}

# カタカナ・ひらがな・英字の対応表（よくある変換パターン）
KANA_ALPHABET_MAPPING = {
    # 英字 -> カタカナ
    "B'z": ["ビーズ", "B'z"],
    "SPITZ": ["スピッツ"],
    "ALFEE": ["アルフィー", "ジアルフィー"],
    "HIKAKIN": ["ヒカキン"],
    "JUJU": ["ジュジュ"],
    "EXILE": ["エグザイル"],
    "Aimer": ["エメ", "エイマー"],

    # カタカナ -> 英字（逆引き用）
    "スピッツ": ["SPITZ", "Spitz"],
    "ビーズ": ["B'z", "Bz"],
    "アルフィー": ["ALFEE", "THE ALFEE"],
    "ジアルフィー": ["ALFEE", "THE ALFEE"],
    "ヒカキン": ["HIKAKIN", "HikaKin"],
    "ジュジュ": ["JUJU", "Juju"],
    "エグザイル": ["EXILE", "Exile"],
    "エメ": ["Aimer"],
    "エイマー": ["Aimer"],

    # 記号・特殊文字の正規化
    "'＝LOVE": ["＝LOVE"],
    "≒JOY": ["JOY"],
    "IS:SUE": ["IS：SUE", "ISSUE"],
}

# 括弧表記の特殊パターン
BRACKET_SPECIAL_CASES = {
    "鈴木一朗（イチロー）": ["イチロー", "鈴木一朗", "鈴木一郎"],
    "SAKURA（宮脇咲良/LE SSERAFIM）": ["宮脇咲良", "SAKURA", "ルセラフィム"],
    "山添寛（相席スタート）": ["山添寛", "相席スタート"],
    "栗谷（カカロニ）": ["栗谷", "カカロニ"],

    # あいまいマッチ成功パターンを逆引き追加
    "横山裕": ["横山裕（SUPER EIGHT(関ジャニ∞))"],
    "堂本剛": ["堂本剛（DOMOTO（KinKi Kids））"],
    "丸山隆平": ["丸山隆平（SUPER EIGHT(関ジャニ∞)）"],
    "村上信五": ["村上信五（SUPER EIGHT(関ジャニ∞)）"],
    "堂本光一": ["堂本光一（DOMOTO（KinKi Kids））"],
    "大倉忠義": ["大倉忠義（SUPER EIGHT(関ジャニ∞)）"],
    "安田章大": ["安田章大（SUPER EIGHT(関ジャニ∞)）"],

    # グループ名の省略パターン
    "＝LOVE": ["'＝LOVE"],
    "JOY": ["≒JOY"],
}

def get_manual_mapping(csv_name: str) -> str:
    """手動マッピング辞書からDB名を取得"""
    return MANUAL_NAME_MAPPING.get(csv_name)

def get_alternative_names(csv_name: str) -> list:
    """代替候補名リストを取得"""
    alternatives = []

    # 手動マッピングをチェック
    manual_name = get_manual_mapping(csv_name)
    if manual_name:
        alternatives.append(manual_name)

    # カナ・英字変換をチェック
    if csv_name in KANA_ALPHABET_MAPPING:
        alternatives.extend(KANA_ALPHABET_MAPPING[csv_name])

    # 括弧特殊ケースをチェック
    for db_name, variants in BRACKET_SPECIAL_CASES.items():
        if csv_name in variants:
            alternatives.append(db_name)

    return alternatives

if __name__ == "__main__":
    # テスト用
    test_names = ["イチロー", "ヒカキン", "B'z", "スピッツ", "THE ALFEE"]

    print("=== タレント名マッピング辞書テスト ===")
    for name in test_names:
        manual = get_manual_mapping(name)
        alternatives = get_alternative_names(name)

        print(f"CSV名: {name}")
        print(f"  手動マッピング: {manual}")
        print(f"  代替候補: {alternatives}")
        print()