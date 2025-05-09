import os
import numpy as np
import pandas as pd
from time import sleep
from datetime import datetime
from read_GIPS_distance import UWBpos
from openpyxl import load_workbook
from pandas import ExcelWriter

# ── 測量設定 ──
actual_distance_cm = 500
measure_times = 20
uwb = UWBpos()
dist_results = []

print(f"📏 測試 anchor6 與目標距離：{actual_distance_cm} cm")
print("🔍 開始測距...\n")

# ── 測距迴圈 ──
for i in range(measure_times):
    dis_to_anchor = uwb.UWB_read()
    raw_value = dis_to_anchor[0]
    dist_cm = raw_value * 100

    if dist_cm < 1:
        print(f"⚠️ 第 {i+1} 次無效資料（{dist_cm:.2f} cm），跳過\n")
        sleep(0.2)
        continue

    print(f"✅ 第 {i+1} 次距離：{dist_cm:.2f} cm\n")
    dist_results.append(round(dist_cm, 2))
    sleep(0.2)

# ── 計算統計值 ──
mean = round(np.mean(dist_results), 2) if dist_results else 0
error = round(mean - actual_distance_cm, 2)
std = round(np.std(dist_results), 2)

# ── 建立單列記錄資料表 ──
timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
row_data = {
    "測試時間": timestamp,
    "測試距離 (cm)": actual_distance_cm,
    "測量值列表 (cm)": ", ".join(map(str, dist_results)),
    "平均距離 (cm)": mean,
    "誤差 (cm)": error,
    "標準差 (cm)": std
}
df_row = pd.DataFrame([row_data])

# ── 儲存到 Excel ──
output_dir = "/home/e520/uwb_results"
os.makedirs(output_dir, exist_ok=True)
excel_path = os.path.join(output_dir, "UWB測距記錄.xlsx")

# 如果檔案存在，就加一列；否則建立新檔
if os.path.exists(excel_path):
    existing_df = pd.read_excel(excel_path)
    new_df = pd.concat([existing_df, df_row], ignore_index=True)
else:
    new_df = df_row

# 寫入 Excel
new_df.to_excel(excel_path, index=False)
print(f"📂 測距資料已追加至：{excel_path}")
