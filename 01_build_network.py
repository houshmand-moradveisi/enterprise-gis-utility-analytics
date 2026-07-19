# 01_build_network.py
import os
import pickle
import geopandas as gpd
import networkx as nx
from shapely.geometry import LineString, MultiLineString, Point
from scipy.spatial import cKDTree
import numpy as np
import config

print("=== STEP 1: LOADING GIS LAYERS (DYNAMIC FEEDER VERSION) ===")
os.makedirs(config.OUTPUT_DIR, exist_ok=True)
CRS = config.CRS_EPSG
SNAP_TOL = 2.0      # تلرانس ۲ متری برای اتصال خطوط به یکدیگر
DEVICE_TOL = 5.0    # تلرانس ۵ متری برای پیدا کردن و چسباندن تجهیزات به خطوط

# 📌 نام واقعی لایه نقطه‌ای فیدر شما در دیتابیس
FEEDER_LAYER_NAME = "FEEDER" 

# بارگذاری لایه خطوط اصلی
lines = gpd.read_file(config.GDB_PATH, layer="OV_HDMVL").to_crs(CRS)

G = nx.Graph()
node_map = {}
node_id = 0

def key(x, y):
    return (round(x, 2), round(y, 2))

def add_node(x, y):
    global node_id
    k = key(x, y)
    if k in node_map:
        return node_map[k]
    node_map[k] = node_id
    G.add_node(node_id, x=x, y=y, type="normal")
    node_id += 1
    return node_id - 1

def explode(geom):
    if isinstance(geom, LineString): return [geom]
    if isinstance(geom, MultiLineString): return list(geom.geoms)
    return []

print("Extracting original coordinates from GIS...")
all_points = []
for geom in lines.geometry:
    if geom is None: continue
    for part in explode(geom):
        for c in part.coords:
            all_points.append(c)

print("Building spatial topology with KDTree...")
points_array = np.array(all_points)
tree = cKDTree(points_array)
clusters = tree.query_ball_tree(tree, r=SNAP_TOL)

cluster_map = {}
for i, neighbors in enumerate(clusters):
    center = points_array[neighbors].mean(axis=0)
    cluster_map[i] = (round(center[0], 2), round(center[1], 2))

coord_to_cluster = {tuple(pt): cluster_map[i] for i, pt in enumerate(all_points)}

print("Generating network topology (Edges)...")
for geom in lines.geometry:
    if geom is None: continue
    for part in explode(geom):
        coords = list(part.coords)
        for i in range(len(coords) - 1):
            p1 = coord_to_cluster[tuple(coords[i])]
            p2 = coord_to_cluster[tuple(coords[i+1])]
            
            n1 = add_node(*p1)
            n2 = add_node(*p2)
            
            if n1 == n2: continue
            dist = Point(p1).distance(Point(p2))
            G.add_edge(n1, n2, weight=dist)

# ساخت یک KDTree ثانویه از نودهای ساخته شده گراف برای اسنپ کردن تجهیزات و پست
graph_nodes_ids = list(G.nodes())
graph_nodes_coords = np.array([[G.nodes[n]["x"], G.nodes[n]["y"]] for n in graph_nodes_ids])
graph_tree = cKDTree(graph_nodes_coords)

print("Attaching electrical devices to nearest nodes (Spatial Join)...")
def attach_devices_spatial(layer_name, attribute_name):
    try:
        df = gpd.read_file(config.GDB_PATH, layer=layer_name).to_crs(CRS)
        attached_count = 0
        for geom in df.geometry:
            if geom is None: continue
            device_coord = np.array([geom.x, geom.y])
            distance, index = graph_tree.query(device_coord, distance_upper_bound=DEVICE_TOL)
            if distance < float('inf'):
                target_node_id = graph_nodes_ids[index]
                G.nodes[target_node_id][attribute_name] = True
                G.nodes[target_node_id]["type"] = attribute_name.lower()
                attached_count += 1
        print(f"-> Successfully attached {attached_count} {layer_name} to nearest graph nodes.")
    except Exception as e:
        print(f"-> Warning: Could not load or process {layer_name}: {e}")

attach_devices_spatial("RECLOSER", "recloser")
attach_devices_spatial("FUSE", "fuse")
attach_devices_spatial("AUT_SWCH", "switch")

print("Auto-Detecting Feeder Source from GIS Layer...")
try:
    feeder_df = gpd.read_file(config.GDB_PATH, layer=FEEDER_LAYER_NAME).to_crs(CRS)
    if not feeder_df.empty:
        feeder_geom = feeder_df.geometry.iloc[0]
        feeder_coord = np.array([feeder_geom.x, feeder_geom.y])
        
        # شعاع جستجوی ۱۰۰ متری برای تضمین اسنپ فیدر به شبکه خطوط
        distance, index = graph_tree.query(feeder_coord, distance_upper_bound=100.0)
        
        if distance < float('inf'):
            real_source_node = graph_nodes_ids[index]
            G.nodes[real_source_node]["type"] = "substation"
            print(f"✔ SUCCESS: Feeder Source locked at Node ID: {real_source_node} (Distance: {round(distance, 2)}m)")
        else:
            print("❌ ERROR: Feeder point found but it is further than 100m away from any line.")
    else:
        print("❌ ERROR: Feeder layer is empty.")
except Exception as e:
    print(f"❌ CRITICAL ERROR: Could not read layer '{FEEDER_LAYER_NAME}': {e}")

G.remove_edges_from(nx.selfloop_edges(G))

with open(config.NETWORK_FILE, "wb") as f:
    pickle.dump(G, f)

print(f"\n=== DONE: Graph Saved Successfully ===")
print(f"Nodes: {G.number_of_nodes()} | Edges: {G.number_of_edges()}")