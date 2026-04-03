import os
import sys

# Replicate core.py path logic
__file__ = r"C:\Users\hp\Desktop\New_ML\JUDAH\engine\core.py"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
horizon = 7
model_path = os.path.join(DATA_DIR, "models", f"xgb_direction_{horizon}d.pkl")

print(f"File: {__file__}")
print(f"Data Dir: {DATA_DIR}")
print(f"Model Path: {model_path}")
print(f"Exists: {os.path.exists(model_path)}")

# Check real files
models_dir = r"C:\Users\hp\Desktop\New_ML\JUDAH\data\models"
if os.path.exists(models_dir):
    print(f"Contents of {models_dir}: {os.listdir(models_dir)}")
else:
    print(f"ERROR: {models_dir} does not exist!")
