import os
import numpy as np
import pandas as pd
from time import sleep
from datetime import datetime
from read_GIPS_distance import UWBpos
from pandas import ExcelWriter

# ── 參數設定 ──
actual_distance_cm = 2000           # 預設測試距離
measure_times = 5                     # 每輪測量次數
total_rounds = 100                     # 總共執行 100 輪
output_dir = "/home/e520/uwb_results"  # 儲存路徑
excel_path = os.path.join(output_dir, "UWB測距記錄木頭遮蔽.xlsx")

# ── 建立儲存資料夾 ──
os.makedirs(output_dir, exist_ok=True)

# ── 初始化 UWB 裝置 ──
uwb = UWBpos()

for round_num in range(1, total_rounds + 1):
    dist_results = []
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print(f"\n🧪 第 {round_num}/{total_rounds} 輪測試開始：{timestamp}")

    # ── 測距迴圈 ──
    for i in range(measure_times):
        dis_to_anchor = uwb.UWB_read()
        raw_value = dis_to_anchor[0]
        dist_cm = raw_value * 100

        if dist_cm < 1:
            print(f"⚠️ 第 {i+1} 次無效資料（{dist_cm:.2f} cm），跳過")
            sleep(0.2)
            continue

        print(f"✅ 第 {i+1} 次距離：{dist_cm:.2f} cm")
        dist_results.append(round(dist_cm, 2))
        sleep(0.2)

    # ── 統計值計算 ──
    mean = round(np.mean(dist_results), 2) if dist_results else 0
    error = round(mean - actual_distance_cm, 2)
    std = round(np.std(dist_results), 2)

    # ── 整理一列資料 ──
    row_data = {
        "測試時間": timestamp,
        "測試距離 (cm)": actual_distance_cm,
        "測量值列表 (cm)": ", ".join(map(str, dist_results)),
        "平均距離 (cm)": mean,
        "誤差 (cm)": error,
        "標準差 (cm)": std
    }
    df_row = pd.DataFrame([row_data])

    # ── 將資料追加到 Excel ──
    if os.path.exists(excel_path):
        existing_df = pd.read_excel(excel_path)
        new_df = pd.concat([existing_df, df_row], ignore_index=True)
    else:
        new_df = df_row

    new_df.to_excel(excel_path, index=False)
    print(f"✅ 結果已儲存至：{excel_path}")
    print("🔁 等待 1 秒進入下一輪測距...\n")
    sleep(1)

print("\n✅ 已完成 100 輪測距，程式自動結束。")
