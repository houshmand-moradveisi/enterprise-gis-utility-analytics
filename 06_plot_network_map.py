# 06_plot_network_map.py
import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import config

print("==========================================================")
print("=== STEP 6: GENERATING RISK-OVERLAY GEOSPATIAL MAP ======")
print("==========================================================")

KOMASI_EXCEL = r"D:\Gis\power_network_project\KOMASI_Specific_Outages.xlsx"

if not os.path.exists(config.NETWORK_FILE):
    print(f"❌ Error: Network graph file not found.")
    exit()

with open(config.NETWORK_FILE, "rb") as f:
    G = pickle.load(f)

df_outages = pd.read_excel(KOMASI_EXCEL) if os.path.exists(KOMASI_EXCEL) else pd.DataFrame()

plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(14, 14), facecolor='#1e1e1e')
ax.set_facecolor('#1e1e1e')

# استخراج دقیق لوکیشن ۴۸۵۲ نود پایه شما بدون نقص هندسی
pos = {n: (data['x'], data['y']) for n, data in G.nodes(data=True) if 'x' in data and 'y' in data}

print("-> Drawing infrastructure network layers...")
nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#00ffcc', alpha=0.3, width=0.6)
nx.draw_networkx_nodes(G, pos, ax=ax, node_size=1, node_color='#666666', alpha=0.5)

# لایه‌نشانی نقاط قرمز رنگ حوادث واقعی روی نودهای متناظر
if not df_outages.empty:
    print("-> Overlaying historical outage hotspots...")
    valid_fault_nodes = [int(n) for n in df_outages['Matched_Node_ID'].unique() if n in pos]
    
    if valid_fault_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=valid_fault_nodes, ax=ax, node_size=35, 
                               node_color='#ff3333', edgecolors='#ffffff', linewidths=0.5, 
                               label='Verified 121 Fault Locations')

ax.set_title("KOMASI FEEDER DIGITAL TWIN\nRisk Hotspots & Geospatial Topology Analysis", 
             color='white', fontsize=14, fontweight='bold', pad=20)
ax.axis('off')

if not df_outages.empty and valid_fault_nodes:
    legend = plt.legend(loc='lower left', scatterpoints=1, fontsize=11, facecolor='#2d2d2d', edgecolor='#444444')
    for text in legend.get_texts():
        text.set_color("white")

map_path = os.path.join(config.OUTPUT_DIR, "komasi_risk_spatial_map.png")
plt.tight_layout()
plt.savefig(map_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()

print(f"\n✔ SUCCESS: High-resolution dark risk map saved to -> {map_path}")
print("==========================================================")