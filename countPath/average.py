import os
import numpy as np
import pandas as pd
from time import sleep
from read_GIPS_distance import UWBpos  # 根據你的檔名修改

# ── 測量參數設定 ──
actual_distance_cm = 600  # 真實距離（公分）
measure_times      = 20   # 測量次數

# ── 初始化 UWB 裝置與結果容器 ──
uwb = UWBpos()
dist_results = []

print(f"📏 測試 anchor6 與目標間距離，預設真實距離為 {actual_distance_cm} cm")
print("🔍 開始測距...\n")

# ── 執行測距迴圈 ──
for i in range(measure_times):
    dis_to_anchor = uwb.UWB_read()    # 假設回傳 [d1, d2, d3…]
    raw_value     = dis_to_anchor[0]  # 只取第 0 個 anchor
    dist_cm       = raw_value * 100   # 從公尺轉公分

    # 過濾異常值
    if dist_cm < 1:
        print(f"⚠️ 第 {i+1} 次無效資料（{dist_cm:.2f} cm），跳過\n")
        sleep(0.2)
        continue

    print(f"✅ 第 {i+1} 次距離：{dist_cm:.2f} cm\n")
    dist_results.append(dist_cm)
    sleep(0.2)

# ── 統計分析 ──
mean  = np.mean(dist_results)
error = mean - actual_distance_cm
std   = np.std(dist_results)

print("📊 測試結果統計：")
print(f"🖩 有效測距次數：{len(dist_results)}")
print(f"📏 平均距離：{mean:.2f} cm")
print(f"📉 誤差：{error:.2f} cm")
print(f"📐 標準差：{std:.2f} cm\n")

# ── 匯出成 Excel 並自動開啟 ──
# 1) 指定已存在的資料夾與檔名
folder_path = r"C:\distance_data"
filename    = "test1.xlsx"
excel_path  = os.path.join(folder_path, filename)

# 2) 建立 pandas DataFrame
df = pd.DataFrame({
    "測距次序": list(range(1, len(dist_results) + 1)),
    "距離 (cm)": dist_results
})

# 3) 寫入 Excel（需先 pip install pandas openpyxl）
df.to_excel(excel_path, index=False, engine="openpyxl")
print(f"✅ 結果已存成 Excel：{excel_path}")

# 4) 自動以預設程式開啟（Windows 專用）
try:
    os.startfile(excel_path)
except Exception as e:
    print("⚠️ 無法自動開啟檔案，請手動前往該路徑打開。", e)
