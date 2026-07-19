# config.py
import os

# مسیر دیتابیس کماسی مریوان
GDB_PATH = r"D:\Gis\data\gdbkomasi\gdbkomasi\gdbkomasi.gdb"

# مسیر پوشه خروجی‌ها
OUTPUT_DIR = r"D:\Gis\power_network_project\outputs"

# مسیر فایل باینری گراف شبکه
NETWORK_FILE = os.path.join(OUTPUT_DIR, "network_graph.pkl")

# سیستم تصویر متری مریوان
CRS_EPSG = "EPSG:32638"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)