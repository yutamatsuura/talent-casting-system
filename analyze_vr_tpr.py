import pandas as pd
import os

def analyze_vr_tpr_data():
    base_path = "/Users/lennon/projects/talent-casting-form-backup-2025-11-30_詳細ページ実行前/DB情報"

    print("=" * 60)
    print("VR・TPRデータ構造分析")
    print("=" * 60)

    # VRデータの分析
    vr_path = os.path.join(base_path, "【VR①】C列の人気度と、E～K列の各種イメージを採用する想定です")
    print(f"\n🎯 VRデータ分析:")
    print(f"フォルダパス: {vr_path}")

    vr_files = [f for f in os.listdir(vr_path) if f.endswith('.csv')]
    print(f"CSVファイル数: {len(vr_files)}")

    if vr_files:
        # 最初のVRファイルを詳細分析
        sample_vr_file = vr_files[0]
        print(f"\n【サンプル分析: {sample_vr_file}】")

        try:
            df_vr = pd.read_csv(os.path.join(vr_path, sample_vr_file), encoding='shift_jis')
            print(f"  行数: {len(df_vr)}")
            print(f"  列数: {len(df_vr.columns)}")
            print(f"  カラム一覧:")
            for i, col in enumerate(df_vr.columns):
                print(f"    {i+1:2d}. {col}")
                # サンプルデータを表示
                non_null_values = df_vr[col].dropna()
                if len(non_null_values) > 0:
                    sample = str(non_null_values.iloc[0])[:40]
                    print(f"        例: {sample}")

            # 重要そうなデータのサンプル表示
            print(f"\n  先頭5行のデータサンプル:")
            print(df_vr.head(3).to_string(max_cols=8))

        except Exception as e:
            print(f"  エラー: {e}")

    # TPRデータの分析
    tpr_path = os.path.join(base_path, "【TPR】G列のパワースコアを採用する想定です")
    print(f"\n\n📊 TPRデータ分析:")
    print(f"フォルダパス: {tpr_path}")

    tpr_files = [f for f in os.listdir(tpr_path) if f.endswith('.csv')]
    print(f"CSVファイル数: {len(tpr_files)}")

    if tpr_files:
        # 最初のTPRファイルを詳細分析
        sample_tpr_file = tpr_files[0]
        print(f"\n【サンプル分析: {sample_tpr_file}】")

        try:
            df_tpr = pd.read_csv(os.path.join(tpr_path, sample_tpr_file), encoding='shift_jis')
            print(f"  行数: {len(df_tpr)}")
            print(f"  列数: {len(df_tpr.columns)}")
            print(f"  カラム一覧:")
            for i, col in enumerate(df_tpr.columns):
                print(f"    {i+1:2d}. {col}")
                # サンプルデータを表示
                non_null_values = df_tpr[col].dropna()
                if len(non_null_values) > 0:
                    sample = str(non_null_values.iloc[0])[:40]
                    print(f"        例: {sample}")

            # 重要そうなデータのサンプル表示
            print(f"\n  先頭5行のデータサンプル:")
            print(df_tpr.head(3).to_string(max_cols=8))

        except Exception as e:
            print(f"  エラー: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    analyze_vr_tpr_data()