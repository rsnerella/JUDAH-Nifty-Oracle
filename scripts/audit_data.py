import os
import pandas as pd

def audit_project(name, data_dir, trainer_file, feature_list_name):
    print(f"\n{'='*20} {name} AUDIT {'='*20}")
    
    # 1. Load Trainer Content to check connectivity
    with open(trainer_file, 'r', encoding='utf-8') as f:
        trainer_content = f.read()

    results = []
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    for f in csv_files:
        path = os.path.join(data_dir, f)
        size_kb = os.path.getsize(path) / 1024
        
        row_count = 0
        try:
            df = pd.read_csv(path)
            row_count = len(df)
        except:
            row_count = "ERROR"

        # Connectivity Check
        # Check if the filename is in the trainer file (indicates it's loaded)
        is_loaded = (f in trainer_content) or (f.replace('_daily.csv', '') in trainer_content)
        
        # Check if features from this file are in the feature list
        # (Very rough check: use the file prefix)
        prefix = f.replace('_daily.csv', '').replace('_CSV', '').replace('.csv', '')
        is_wired = f"'{prefix}" in trainer_content or f'"{prefix}' in trainer_content or f"_{prefix}" in trainer_content

        results.append({
            "File": f,
            "Size (KB)": round(size_kb, 1),
            "Rows": row_count,
            "Loaded?": "✅" if is_loaded else "❌",
            "Wired?": "✅" if is_wired else "❌"
        })

    df_results = pd.DataFrame(results)
    print(df_results.to_markdown(index=False))
    
    # Check for missing paths
    print(f"\n--- Integrity Check ---")
    if any(df_results['Rows'] == 0):
        print("⚠️ WARNING: Found empty files (0 rows).")
    if any(df_results['Size (KB)'] < 0.5):
        print("⚠️ WARNING: Found suspiciously small files (< 0.5KB).")

if __name__ == "__main__":
    # JUDAH Audit
    audit_project(
        "JUDAH", 
        r"c:\Users\hp\Desktop\New_ML\JUDAH-Nifty-Oracle-main\data",
        r"c:\Users\hp\Desktop\New_ML\JUDAH-Nifty-Oracle-main\engine\core.py",
        "FEATURE_COLS"
    )
    
    # MOSES Audit
    audit_project(
        "MOSES", 
        r"c:\Users\hp\Desktop\New_ML\Moses-RandomForest\data",
        r"c:\Users\hp\Desktop\New_ML\Moses-RandomForest\rf_trainer.py",
        "DIRECTION_FEATURES"
    )
