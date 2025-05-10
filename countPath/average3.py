import os
import numpy as np
import pandas as pd
from time import sleep
from datetime import datetime
from read_GIPS_distance import UWBpos

# ── 參數設定 ──
actual_distance_cm = 400               # 預設測試距離
measure_times     = 10                  # 每輪測量次數
total_rounds      = 100                 # 總共執行 100 輪
output_dir        = "/home/e520/uwb_results"  # 儲存路徑
excel_path        = os.path.join(output_dir, "UWB測距記錄總表.xlsx")

# ── 建立儲存資料夾 ──
os.makedirs(output_dir, exist_ok=True)

# ── 初始化 UWB 裝置 ──
uwb = UWBpos()

for round_num in range(1, total_rounds + 1):
    results_0 = []  # Anchor 0 的測量值列表
    results_1 = []  # Anchor 1 的測量值列表
    results_2 = []  # Anchor 2 的測量值列表
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print(f"\n🧪 第 {round_num}/{total_rounds} 輪測試開始：{timestamp}")

    # ── 測距迴圈 ──
    for i in range(measure_times):
        dis   = uwb.UWB_read()   # 回傳至少三個元素
        dist0 = dis[0] * 100     # Anchor 0（cm）
        dist1 = dis[1] * 100     # Anchor 1（cm）
        dist2 = dis[2] * 100     # Anchor 2（cm）

        # 如果有任一無效 (<1cm)，就跳過
        if dist0 < 1 or dist1 < 1 or dist2 < 1:
            print(f"⚠️ 第 {i+1} 次無效資料，跳過 (A0={dist0:.2f}, A1={dist1:.2f}, A2={dist2:.2f} cm)")
            sleep(0.2)
            continue

        print(f"✅ 第 {i+1} 次距離：A0={dist0:.2f} cm, A1={dist1:.2f} cm, A2={dist2:.2f} cm")
        results_0.append(round(dist0, 2))
        results_1.append(round(dist1, 2))
        results_2.append(round(dist2, 2))
        sleep(0.2)

    # ── 統計值計算 ──
    mean0 = round(np.mean(results_0), 2) if results_0 else 0
    mean1 = round(np.mean(results_1), 2) if results_1 else 0
    mean2 = round(np.mean(results_2), 2) if results_2 else 0

    err0  = round(mean0 - actual_distance_cm, 2)
    err1  = round(mean1 - actual_distance_cm, 2)
    err2  = round(mean2 - actual_distance_cm, 2)

    std0  = round(np.std(results_0), 2)
    std1  = round(np.std(results_1), 2)
    std2  = round(np.std(results_2), 2)

    # ── 整理一列資料 ──
    row = {
        "測試時間":            timestamp,
        "測試距離 (cm)":       actual_distance_cm,
        "測量值列表 A0 (cm)":   ", ".join(map(str, results_0)),
        "平均距離 A0 (cm)":    mean0,
        "誤差 A0 (cm)":        err0,
        "標準差 A0 (cm)":      std0,
        "測量值列表 A1 (cm)":   ", ".join(map(str, results_1)),
        "平均距離 A1 (cm)":    mean1,
        "誤差 A1 (cm)":        err1,
        "標準差 A1 (cm)":      std1,
        "測量值列表 A2 (cm)":   ", ".join(map(str, results_2)),
        "平均距離 A2 (cm)":    mean2,
        "誤差 A2 (cm)":        err2,
        "標準差 A2 (cm)":      std2,
    }
    df_row = pd.DataFrame([row])

    # ── 追加到 Excel ──
    if os.path.exists(excel_path):
        df_all = pd.concat([pd.read_excel(excel_path), df_row], ignore_index=True)
    else:
        df_all = df_row

    df_all.to_excel(excel_path, index=False)
    print(f"✅ 第 {round_num} 輪結果已儲存至：{excel_path}")
    print("🔁 等待 5 秒進入下一輪測距...\n")
    sleep(5)

print("\n✅ 已完成所有測距輪次，程式結束。")
