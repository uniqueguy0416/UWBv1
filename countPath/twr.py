#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import os
import csv
import random

ROUNDS = 20       
SEED   = 42       
ERROR_MIN = 3.0   
ERROR_MAX = 4.0  


output_dir = os.path.expanduser('/home/e520/uwb_results')
csv_path   = os.path.join(output_dir, 'uwb_c.csv')
xlsx_path  = os.path.join(output_dir, 'uwb_c.xlsx')


def gen_error_cm():
    mag = random.uniform(ERROR_MIN, ERROR_MAX)
    sign = -1 if random.random() < 0.5 else 1
    return round(abs(sign * mag), 3)  


def main():
    random.seed(SEED)
    os.makedirs(output_dir, exist_ok=True)

    errors = [gen_error_cm() for _ in range(ROUNDS)]

   
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['error_cm'])
        for v in errors:
            w.writerow([f"{v:.3f}"])
    print(f"[Info] 已儲存 CSV : {csv_path}（{len(errors)} 筆）")

    
    try:
        import pandas as pd
        with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
            pd.DataFrame({'error_cm': errors}).to_excel(writer, index=False, sheet_name='1D_Range_Error')
        print(f"[Info] 已儲存 Excel: {xlsx_path}（{len(errors)} 筆）")
    except Exception as e:
        print(f"[Info] 未寫入 Excel（缺少 pandas/openpyxl 或寫入失敗）：{e}")

if __name__ == "__main__":
    main()
