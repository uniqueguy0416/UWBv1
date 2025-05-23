import os
import numpy as np
import pandas as pd
from time import sleep
from datetime import datetime
from read_GIPS_distance import UWBpos

# ── 參數設定 ──
actual_distance_cm = 400               # 預設測試距離
measure_times     = 10                 # 每輪測量次數
total_rounds      = 100                # 總共執行 100 輪
output_dir        = "/home/e520/uwb_results"
excel_path        = os.path.join(output_dir, "UWB測距記錄總表.xlsx")

# ── 建立儲存資料夾 ──
os.makedirs(output_dir, exist_ok=True)

# ── 初始化 UWB 裝置 ──
uwb = UWBpos()

for round_num in range(1, total_rounds + 1):
    results_0, results_1, results_2 = [], [], []
    pos_x_list, pos_y_list = [], []           # 用來存每次算出的相對座標
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print(f"\n🧪 第 {round_num}/{total_rounds} 輪測試開始：{timestamp}")

    # ── 測距迴圈 ──
    for i in range(measure_times):
        diss = uwb.UWB_read()   # 回傳 mat 距離陣列（m）
        # 若有任何小於 0.01 m 就當作無效
        if any(d < 0.01 for d in diss):
            print(f"⚠️ 第 {i+1} 次無效資料，跳過")
            sleep(0.2)
            continue

        # 1) 距離紀錄 (cm)
        d0, d1, d2 = (diss * 100).round(2)
        results_0.append(d0); results_1.append(d1); results_2.append(d2)

        # 2) 直接計算當次相對坐標 (m)
        x_rel, y_rel = uwb.compute_relative()
        pos_x_list.append(x_rel)
        pos_y_list.append(y_rel)

        print(f"✅ 第 {i+1} 次：A0={d0:.2f}cm, A1={d1:.2f}cm, A2={d2:.2f}cm → (x,y)=({x_rel:.3f},{y_rel:.3f}) m")
        sleep(0.2)

    # ── 統計值與平均坐標 ──
    mean0 = np.mean(results_0) if results_0 else 0
    mean1 = np.mean(results_1) if results_1 else 0
    mean2 = np.mean(results_2) if results_2 else 0

    err0 = mean0 - actual_distance_cm
    err1 = mean1 - actual_distance_cm
    err2 = mean2 - actual_distance_cm

    std0 = np.std(results_0) if results_0 else 0
    std1 = np.std(results_1) if results_1 else 0
    std2 = np.std(results_2) if results_2 else 0

    # 新增：計算平均相對座標
    x_mean = np.mean(pos_x_list) if pos_x_list else 0
    y_mean = np.mean(pos_y_list) if pos_y_list else 0

    # ── 準備寫入一列資料 ──
    row = {
        "測試時間":          timestamp,
        "測試距離 (cm)":     actual_distance_cm,
        "平均距離 A0 (cm)":  round(mean0,2),
        "誤差 A0 (cm)":      round(err0,2),
        "標準差 A0 (cm)":    round(std0,2),
        "平均距離 A1 (cm)":  round(mean1,2),
        "誤差 A1 (cm)":      round(err1,2),
        "標準差 A1 (cm)":    round(std1,2),
        "平均距離 A2 (cm)":  round(mean2,2),
        "誤差 A2 (cm)":      round(err2,2),
        "標準差 A2 (cm)":    round(std2,2),
        # 以下是新增的欄位
        "平均 X (m)":        round(x_mean,3),
        "平均 Y (m)":        round(y_mean,3),
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
