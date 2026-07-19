# 02_save_load_network.py
import pickle
import config

print("=== STEP 2: VERIFYING NETWORK FILE ===")
try:
    with open(config.NETWORK_FILE, "rb") as f:
        G = pickle.load(f)
    print("✔ Network loaded successfully!")
    print(f"Total Verified Nodes: {G.number_of_nodes()}")
    print(f"Total Verified Edges: {G.number_of_edges()}")
except FileNotFoundError:
    print("❌ Error: network.pkl not found! Run step 1 first.")