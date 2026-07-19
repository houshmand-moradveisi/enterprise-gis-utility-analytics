# 04_visualize_network.py
import os
import pickle
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
from pyproj import Transformer
import config

print("==========================================================")
print("=== STEP 4: INTEGRATING REAL MARIVAN OUTAGES TO GRAPH ===")
print("==========================================================")

OUTAGE_EXCEL = r"D:\Gis\power_network_project\Outages_Marivan.xlsx"
OUTPUT_EXCEL = r"D:\Gis\power_network_project\KOMASI_Specific_Outages.xlsx"

if not os.path.exists(config.NETWORK_FILE):
    print(f"❌ Error: Graph model database not found.")
    exit()

with open(config.NETWORK_FILE, "rb") as f:
    G = pickle.load(f)

# استخراج دقیق مختصات ۴۸۵۲ نود اصلی شما برای اسنپ کردن حوادث
graph_nodes_ids = list(G.nodes())
graph_coords = np.array([[G.nodes[n]["x"], G.nodes[n]["y"]] for n in graph_nodes_ids])
graph_tree = cKDTree(graph_coords)

if not os.path.exists(OUTAGE_EXCEL):
    print(f"❌ Error: Source outage excel not found at {OUTAGE_EXCEL}")
    exit()

df_marivan = pd.read_excel(OUTAGE_EXCEL)

# مبدل فرکانسی برای تبدیل درجه به سیستم تصویر متری فیدر شما (UTM 38N)
transformer = Transformer.from_crs("EPSG:4326", config.CRS_EPSG, always_xy=True)
DISTANCE_THRESHOLD = 50.0  # حریم ۵۰ متری بافر خطا برای جی‌پی‌اس تبلت‌ها
komasi_outages = []

print("-> Running Spatial Snapping via cKDTree for 121 Outages...")
for idx, row in df_marivan.iterrows():
    out_x, out_y = transformer.transform(row['GPSX'], row['GPSY'])
    distance, index = graph_tree.query([out_x, out_y])
    
    if distance <= DISTANCE_THRESHOLD:
        target_node = graph_nodes_ids[index]
        komasi_outages.append({
            'OutageID': row['شماره خاموشی'],
            'Date': row['تاریخ'],
            'Time': row['ساعت'],
            'Worker': row['استادکار'],
            'Matched_Node_ID': target_node,
            'Distance_Meters': round(distance, 2)
        })

df_komasi_outages = pd.DataFrame(komasi_outages)
print(f"\n✔ SPATIAL MATCHING COMPLETE:")
print(f"-> Out of 700 Marivan raw outages, {len(df_komasi_outages)} specific events are bound to KOMASI feeder.")

# ثبت فراوانی تعداد حوادث به عنوان ویژگی در داخل نودهای گراف اصلی
for n in G.nodes():
    G.nodes[n]['real_outages_count'] = 0

for _, row in df_komasi_outages.iterrows():
    node_id = int(row['Matched_Node_ID'])
    G.nodes[node_id]['real_outages_count'] += 1

# ذخیره گراف غنی شده و فایل اکسل ۴۹ تایی کماسی
with open(config.NETWORK_FILE, "wb") as f:
    pickle.dump(G, f)

df_komasi_outages.to_excel(OUTPUT_EXCEL, index=False)
print(f"✔ SUCCESS: Project database updated. Specific file saved to: '{OUTPUT_EXCEL}'")
print("==========================================================")