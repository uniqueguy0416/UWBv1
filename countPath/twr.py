#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UWB Anchor-Tag 1D TWR 誤差量測（單一 Anchor；僅輸出 error_cm）
--------------------------------------------------------------
• 沿用你原本的程式結構與輸出路徑/檔名
• 將多錨點/least_squares 全移除，改為單一 Anchor 距離 → 誤差
• 只輸出一欄：error_cm（cm）
"""

import os
import serial
import numpy as np
import pandas as pd
from datetime import datetime

# 1. 單一 Anchor ID 與位置 (x, y, z) —— 保留你的變數命名，但只放一顆
anchor_ids = [
    '0241000000000000',  # Anchor6
]
anchor_labels = ['anchor6']
anchor_positions = [
    (4.00, 0.00, 2),
]

# 2. Tag 真實放置座標
tag_pos = (2.5, 4.0, 1.0)

# 3. 量測次數與串口參數
ROUNDS = 10
PORT = '/dev/ttyUSB0'
BAUD = 57600

# 4. 建立串口連線
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"[Info] Connected to {PORT} @ {BAUD}bps")
except Exception as e:
    print(f"[Warning] 無法開啟串口 {PORT}: {e}")
    ser = None

def read_distance_one(serial_iface, aid, read_len=1024, retries=20):
    """
    讀單一 Anchor 距離（m）
    - 在 raw hex 中尋找 8-byte Anchor ID 後 4 bytes（小端）距離(cm)
    - 放大讀取長度、加入重試，提升成功率
    """
    if not serial_iface:
        return 0.0
    aid_hex = aid.lower()
    for _ in range(retries):
        raw = serial_iface.read(read_len)
        if not raw:
            continue
        raw_hex = raw.hex()
        idx = raw_hex.find(aid_hex)
        if idx >= 0:
            hex_dis = raw_hex[idx + 16: idx + 24]  # ID(16 hex) 後的8 hex 為距離(cm, little-endian)
            try:
                cm = int.from_bytes(bytes.fromhex(hex_dis)[::-1], 'big')
            except ValueError:
                cm = 0
            if 0 < cm < 32768:
                return cm / 100.0  # m
    return 0.0

def main():
    errors = []

    # 單一 Anchor 與 Tag 的真實距離
    true_d = float(np.linalg.norm(
        np.array(anchor_positions[0]) - np.array(tag_pos)
    ))

    for i in range(ROUNDS):
        meas_d = read_distance_one(ser, anchor_ids[0])
        if meas_d <= 0.0:
            print(f"{i+1:04d}  讀取失敗，略過")
            continue

        err_cm = (meas_d - true_d) * 100.0
        errors.append(round(err_cm, 3))
        print(f"{i+1:04d}  error_cm={err_cm:.3f}")

    if ser:
        ser.close()

    # === 輸出（沿用你原本的路徑與檔名）===
    output_dir = os.path.expanduser('/home/e520/uwb_results')
    os.makedirs(output_dir, exist_ok=True)
    csv_path  = os.path.join(output_dir, 'uwb_線性線性_含估計座標.csv')
    xlsx_path = os.path.join(output_dir, 'uwb_線性_含估計座標.xlsx')

    df = pd.DataFrame({'error_cm': errors})
    df.to_csv(csv_path, index=False)
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='1D_Range_Error')

    print(f"[Info] 已儲存 CSV: {csv_path}")
    print(f"[Info] 已儲存 Excel: {xlsx_path}（{len(df)} 筆 error_cm）")

if __name__ == "__main__":
    main()
