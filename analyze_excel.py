import pandas as pd
import os

def analyze_excel_structure():
    # Excelファイルのパスを指定
    excel_path = "/Users/lennon/projects/talent-casting-form-backup-2025-11-30_詳細ページ実行前/DB情報/Nowデータ_20251126.xlsx"

    print(f"ファイル存在確認: {os.path.exists(excel_path)}")
    print(f"ファイルサイズ: {os.path.getsize(excel_path) / (1024*1024):.2f} MB")

    try:
        # Excelファイルのシート名を取得
        excel_file = pd.ExcelFile(excel_path)
        sheet_names = excel_file.sheet_names
        print(f"\nシート数: {len(sheet_names)}")
        print("=" * 50)
        print("シート一覧:")

        for i, sheet in enumerate(sheet_names, 1):
            print(f"  {i}. {sheet}")

            # 各シートの基本情報を取得
            try:
                df = pd.read_excel(excel_path, sheet_name=sheet, nrows=5)  # 最初の5行だけ読み込み
                print(f"     - 行数: {len(pd.read_excel(excel_path, sheet_name=sheet))}")
                print(f"     - 列数: {df.shape[1]}")
                print(f"     - カラム名（最初の10個）: {list(df.columns[:10])}")
                print()
            except Exception as e:
                print(f"     - エラー: {str(e)[:50]}...")
                print()

        print("=" * 50)
        print("主要シートの詳細分析:")

        # 主要そうなシートを詳細分析
        for sheet_name in sheet_names:
            if any(keyword in sheet_name.lower() for keyword in ['talent', 'タレント', 'vr', 'tpr']):
                print(f"\n【{sheet_name}】の詳細:")
                try:
                    df = pd.read_excel(excel_path, sheet_name=sheet_name)
                    print(f"  総データ数: {len(df)}")
                    print(f"  カラム一覧:")
                    for i, col in enumerate(df.columns):
                        print(f"    {i+1:2d}. {col}")
                        # サンプルデータを表示（非nullの最初の値）
                        non_null_values = df[col].dropna()
                        if len(non_null_values) > 0:
                            sample = str(non_null_values.iloc[0])[:30]
                            print(f"        例: {sample}")
                        print()
                except Exception as e:
                    print(f"  エラー: {e}")

                if len(sheet_names) > 10:  # シート数が多い場合は最初のいくつかだけ
                    break

    except Exception as e:
        print(f"メインエラー: {e}")

if __name__ == "__main__":
    analyze_excel_structure()