import json
import traceback

try:
    with open('data/models/offline_robot_brain.json', 'r') as f:
        data = json.load(f)
        
    print("KEYS:", data.keys())
    print("HORIZONS PRESENT:", list(data['horizons'].keys()))
    for h in data['horizons'].keys():
        print(f"Horizon {h} has heatmap:", 'heatmap' in data['horizons'][h])
        if 'heatmap' in data['horizons'][h]:
            print(f"Horizon {h} heatmap len:", len(data['horizons'][h]['heatmap']))
except Exception as e:
    traceback.print_exc()
