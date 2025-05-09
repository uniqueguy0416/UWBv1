import os
import numpy as np
import pandas as pd
from time import sleep
from datetime import datetime
from read_GIPS_distance import UWBpos
from openpyxl import load_workbook
from pandas import ExcelWriter

# ── 測量參數設定 ──
actual_distance_cm = 500
measure_times      = 20

# ── 初始化 ──
uwb = UWBpos()
dist_results = []
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

print(f"📏 測試 anchor6 與目標距離：{actual_distance_cm} cm")
print("🔍 開始測距...\n")

# ── 測距迴圈 ──
for i in range(measure_times):
    dis_to_anchor = uwb.UWB_read()
    raw_value     = dis_to_anchor[0]
    dist_cm       = raw_value * 100

    if dist_cm < 1:
        print(f"⚠️ 第 {i+1} 次無效資料（{dist_cm:.2f} cm），跳過\n")
        sleep(0.2)
        continue

    print(f"✅ 第 {i+1} 次距離：{dist_cm:.2f} cm\n")
    dist_results.append(dist_cm)
    sleep(0.2)

# ── 統計分析 ──
mean  = np.mean(dist_results) if dist_results else 0
error = mean - actual_distance_cm
std   = np.std(dist_results) if dist_results else 0

# ── 建立資料表 ──
df_measure = pd.DataFrame({
    "測距次序": list(range(1, len(dist_results)+1)),
    "距離 (cm)": dist_results
})
df_stats = pd.DataFrame({
    "統計項目": ["平均距離", "誤差", "標準差"],
    "數值 (cm)": [round(mean, 2), round(error, 2), round(std, 2)]
})

# ── 儲存目錄與檔案 ──
output_dir = "/home/e520/uwb_results"
os.makedirs(output_dir, exist_ok=True)
excel_path = os.path.join(output_dir, "UWB測距總表.xlsx")
sheet_name = f"測距_{timestamp}"

# ── 寫入 Excel（追加模式）──
if os.path.exists(excel_path):
    with ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists="replace") as writer:
        df_measure.to_excel(writer, sheet_name=sheet_name, index=False)
        df_stats.to_excel(writer, sheet_name=f"{sheet_name}_統計", index=False)
else:
    with ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_measure.to_excel(writer, sheet_name=sheet_name, index=False)
        df_stats.to_excel(writer, sheet_name=f"{sheet_name}_統計", index=False)

print(f"📂 測距資料已儲存至：{excel_path}")
