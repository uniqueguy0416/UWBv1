import os
import numpy as np
import pandas as pd
from time import sleep
from datetime import datetime
from read_GIPS_distance import UWBpos  # 根據你的檔名修改

# ── 測量參數設定 ──
actual_distance_cm = 200  # 真實距離（公分）
measure_times      = 10   # 測量次數

# ── 初始化 UWB 裝置與結果容器 ──
uwb = UWBpos()
dist_results = []

print(f"📏 測試 anchor6 與目標間距離，預設真實距離為 {actual_distance_cm} cm")
print("🔍 開始測距...\n")

# ── 執行測距迴圈 ──
for i in range(measure_times):
    dis_to_anchor = uwb.UWB_read()    # 假設回傳 [d1, d2, …]
    raw_value     = dis_to_anchor[0]  # 只取第 0 個 anchor
    dist_cm       = raw_value * 100   # 公尺轉公分

    # 過濾異常值
    if dist_cm < 1:
        print(f"⚠️ 第 {i+1} 次無效資料（{dist_cm:.2f} cm），跳過\n")
        sleep(0.2)
        continue

    print(f" 第 {i+1} 次距離：{dist_cm:.2f} cm\n")
    dist_results.append(dist_cm)
    sleep(0.2)

# ── 統計分析 ──
mean  = np.mean(dist_results) if dist_results else 0
error = mean - actual_distance_cm
std   = np.std(dist_results) if dist_results else 0

print(" 測試結果統計：")
print(f"🖩 有效測距次數：{len(dist_results)}")
print(f" 平均距離：{mean:.2f} cm")
print(f" 誤差：{error:.2f} cm")
print(f" 標準差：{std:.2f} cm\n")



# ── 匯出成本地 Excel（含統計資料） ──
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = "/home/e520/uwb_results"
os.makedirs(output_dir, exist_ok=True)  # 若資料夾不存在則建立
local_filename = os.path.join(output_dir, f"UWB測距結果_{timestamp}.xlsx")


# 建立測距資料表格
df_measure = pd.DataFrame({
    "測距次序": list(range(1, len(dist_results) + 1)),
    "距離 (cm)": dist_results
})

# 建立統計資料表格
df_stats = pd.DataFrame({
    "統計項目": ["平均距離", "誤差", "標準差"],
    "數值 (cm)": [round(mean, 2), round(error, 2), round(std, 2)]
})

# 寫入 Excel 的兩個工作表
with pd.ExcelWriter(local_filename, engine="openpyxl") as writer:
    df_measure.to_excel(writer, sheet_name="測距資料", index=False)
    df_stats.to_excel(writer, sheet_name="統計結果", index=False)

print(f" 測距結果已儲存至：{local_filename}")
