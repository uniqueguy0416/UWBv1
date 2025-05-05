import csv
import numpy as np
from time import sleep
from read_GIPS_distance import UWBpos  # 根據你的檔名修改

# ✅ 測量參數設定
actual_distance_cm = 600  # 真實距離（公分）
measure_times = 20         # 測量次數

uwb = UWBpos()
results = []

print(f"📏 測試 anchor6 與目標間距離，預設真實距離為 {actual_distance_cm} cm")
print("🔍 開始測距...\n")

for i in range(measure_times):
    dis_to_anchor = uwb.UWB_read()

    # 只取第 0 個（anchor6）
    raw_value = dis_to_anchor[0]
    print(f"dis[0] read: {raw_value}")

    # 直接當作公分(cm)單位，不需轉換
    dist_cm = raw_value*100

    # 忽略異常值
    if dist_cm < 1:
        print(f"⚠️ 第 {i+1} 次無效資料（{dist_cm:.2f} cm），跳過\n")
        sleep(0.2)
        continue

    print(f"✅ 第 {i+1} 次距離：{dist_cm:.2f} cm\n")
    results.append(dist_cm)
    sleep(0.2)

# 📊 統計分析
mean = np.mean(results)
error = mean - actual_distance_cm
std = np.std(results)
relative_error = abs(error) / actual_distance_cm * 100

print("📊 測試結果統計：")
print(f"🔢 有效測距次數：{len(results)}")
print(f"📏 平均距離：{mean:.2f} cm")
print(f"📉 誤差：{error:.2f} cm")
print(f"📈 相對誤差：{relative_error:.2f} %")
print(f"📐 標準差：{std:.2f} cm\n")

# 💾 存檔
filename = "uwb_precision_test.csv"
with open(filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["測距次數", "距離 (cm)"])
    for i, d in enumerate(results):
        writer.writerow([i + 1, d])

print(f"✅ 測距結果已儲存到：{filename}")
