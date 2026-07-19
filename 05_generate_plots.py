# 05_generate_plots.py
import os
import pandas as pd
import matplotlib.pyplot as plt
import config

print("==========================================================")
print("=== STEP 5: GENERATING MANAGEMENT RESILIENCE CHARTS ===")
print("==========================================================")

KOMASI_EXCEL = r"D:\Gis\power_network_project\KOMASI_Specific_Outages.xlsx"

if not os.path.exists(KOMASI_EXCEL):
    print(f"❌ Error: Specific outage file not found. Run Step 4 first.")
    exit()

df = pd.read_excel(KOMASI_EXCEL)

# نمودار ۱: توزیع اکیپ‌های عملیاتی
plt.figure(figsize=(10, 6))
worker_counts = df['Worker'].value_counts()
bars = worker_counts.plot(kind='bar', color='#1f77b4', edgecolor='black', alpha=0.8)
plt.title("Real-world Outage Distribution by Response Teams (KOMASI Feeder)", fontsize=12, fontweight='bold', pad=15)
plt.ylabel("Number of Resolved Outages")
plt.xlabel("Maintenance Technician (Worker)")
plt.grid(axis='y', linestyle='--', alpha=0.5)

for bar in bars.patches:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.2, f'{int(yval)}', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(config.OUTPUT_DIR, "komasi_outages_by_worker.png"), dpi=300)
plt.close()

# نمودار ۲: تحلیل زمانی (ساعت پیک حوادث)
df['Hour'] = df['Time'].str.split(':').str[0].astype(int)
plt.figure(figsize=(10, 5))
hourly_counts = df['Hour'].value_counts().sort_index().reindex(range(24), fill_value=0)
plt.plot(hourly_counts.index, hourly_counts.values, marker='o', linewidth=2.5, color='#d62728')
plt.fill_between(hourly_counts.index, hourly_counts.values, color='#d62728', alpha=0.15)
plt.title("Hourly Outage Temporal Distribution Peak Analysis", fontsize=12, fontweight='bold', pad=15)
plt.xlabel("Hour of the Day (24h Format)")
plt.ylabel("Failure Occurrence Count")
plt.xticks(range(0, 24))
plt.grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()
plt.savefig(os.path.join(config.OUTPUT_DIR, "komasi_temporal_peaks.png"), dpi=300)
plt.close()

print("✔ SUCCESS: Management charts successfully generated in outputs folder.")
print("==========================================================")