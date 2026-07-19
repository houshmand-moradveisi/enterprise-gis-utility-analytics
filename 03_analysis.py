# 04_visualize_network.py
import pickle
import matplotlib.pyplot as plt
import networkx as nx
import config

print("=== STEP 4: GENERATING HIGH-RESOLUTION NETWORK MAP (COMPATIBLE LAYER ORDER) ===")

with open(config.NETWORK_FILE, "rb") as f:
    G = pickle.load(f)

pos = {n: (data["x"], data["y"]) for n, data in G.nodes(data=True)}

normal_nodes = []
recloser_nodes = []
fuse_nodes = []
switch_nodes = []
substation_nodes = []

for n, data in G.nodes(data=True):
    t = data.get("type", "normal")
    if t == "recloser": recloser_nodes.append(n)
    elif t == "fuse": fuse_nodes.append(n)
    elif t == "switch": switch_nodes.append(n)
    elif t == "substation": substation_nodes.append(n)
    else: normal_nodes.append(n)

plt.figure(figsize=(20, 20), facecolor="#222222") 
ax = plt.gca()
ax.set_facecolor("#222222")

print("Drawing grid lines (Edges)...")
# رسم خطوط و تنظیم اولویت لایه به صورت مستقیم روی آبجکت خروجی مت‌پلات‌لیب
edges_draw = nx.draw_networkx_edges(G, pos, width=0.5, alpha=0.4, edge_color="#cccccc", ax=ax)
if edges_draw is not None:
    edges_draw.set_zorder(1)

print("Drawing grid components (Nodes)...")
# نودهای معمولی
nodes_draw = nx.draw_networkx_nodes(G, pos, nodelist=normal_nodes, node_size=3, node_color="#00ffcc", alpha=0.6, ax=ax)
if nodes_draw is not None:
    nodes_draw.set_zorder(2)

# رکلوزرها
if recloser_nodes:
    rec_draw = nx.draw_networkx_nodes(G, pos, nodelist=recloser_nodes, node_size=140, node_color="#ff3333", node_shape="s", label="Recloser (Protection)", ax=ax)
    if rec_draw is not None: rec_draw.set_zorder(4)

# فیوزها
if fuse_nodes:
    fuse_draw = nx.draw_networkx_nodes(G, pos, nodelist=fuse_nodes, node_size=100, node_color="#ffcc00", node_shape="^", label="Expulsion Fuse", ax=ax)
    if fuse_draw is not None: fuse_draw.set_zorder(4)

# کلیدها
if switch_nodes:
    sw_draw = nx.draw_networkx_nodes(G, pos, nodelist=switch_nodes, node_size=100, node_color="#3399ff", node_shape="D", label="Sectionalizer / Switch", ax=ax)
    if sw_draw is not None: sw_draw.set_zorder(5)

# پست اصلی و نقطه شروع فیدر واقعی (بالاترین اولویت)
if substation_nodes:
    sub_draw = nx.draw_networkx_nodes(G, pos, nodelist=substation_nodes, node_size=450, node_color="#ff00ff", node_shape="*", label="Main Substation (Source)", ax=ax)
    if sub_draw is not None: sub_draw.set_zorder(10)

plt.title("Smart Grid Topology & Asset Vulnerability Analysis", fontsize=20, color="white", pad=20)
legend = plt.legend(loc="lower left", fontsize=14, facecolor="#333333", edgecolor="white")
for text in legend.get_texts():
    text.set_color("white")

plt.axis("equal")
plt.axis("off")
plt.tight_layout()

print("Rendering Map Window...")
plt.show()