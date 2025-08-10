#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UWB Anchor-Tag 1D TWR 誤差量測（假資料版）
-----------------------------------------
• 原程式結構保留，但不連接串口、不讀真實資料
• 直接生成 error_cm 值於 3～4 cm 範圍（正負隨機）
• 只輸出一欄：error_cm
• 輸出檔名與路徑沿用原設定：
  /home/e520/uwb_results/uwb_線性線性_含估計座標.csv
  /home/e520/uwb_results/uwb_線性_含估計座標.xlsx
"""

import os
import csv
import random

# ===== 1. 假資料參數 =====
ROUNDS = 10       # 產生筆數（可調整）
SEED   = 42       # 隨機種子（改掉可換一批數據）
ERROR_MIN = 3.0   # 誤差最小值（cm）
ERROR_MAX = 4.0   # 誤差最大值（cm）

# ===== 2. 輸出設定 =====
output_dir = os.path.expanduser('/home/e520/uwb_results')
csv_path   = os.path.join(output_dir, 'uwb_.csv')
xlsx_path  = os.path.join(output_dir, 'uwb_.xlsx')

# ===== 3. 生成假誤差 =====
def gen_error_cm():
    mag = random.uniform(ERROR_MIN, ERROR_MAX)
    sign = -1 if random.random() < 0.5 else 1
    return round(sign * mag, 3)

def main():
    random.seed(SEED)
    os.makedirs(output_dir, exist_ok=True)

    errors = [gen_error_cm() for _ in range(ROUNDS)]

    # ---- 寫 CSV（必寫）----
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['error_cm'])
        for v in errors:
            w.writerow([f"{v:.3f}"])
    print(f"[Info] 已儲存 CSV : {csv_path}（{len(errors)} 筆）")

    # ---- 寫 Excel（若可用 pandas 就寫）----
    try:
        import pandas as pd
        with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
            pd.DataFrame({'error_cm': errors}).to_excel(writer, index=False, sheet_name='1D_Range_Error')
        print(f"[Info] 已儲存 Excel: {xlsx_path}（{len(errors)} 筆）")
    except Exception as e:
        print(f"[Info] 未寫入 Excel（缺少 pandas/openpyxl 或寫入失敗）：{e}")

if __name__ == "__main__":
    main()
