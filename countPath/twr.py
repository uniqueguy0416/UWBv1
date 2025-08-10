#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UWB Anchor-Tag TWR 誤差量測（精簡版）
-----------------------------------
• 單一 Anchor + 單一 Tag
• 從串口讀取 Anchor 回傳距離（cm，小端）→ 轉 m
• 計算真實距離與 1D range error (cm)
• 只輸出 error_cm 一欄
• 輸出路徑與檔名與原程式相同
"""

import os
import serial
import numpy as np
import pandas as pd

# ===== 1. Anchor 與 Tag 設定 =====
anchor_id  = '0241000000000000'     # Anchor 的 8-byte HEX ID
anchor_pos = (4.00, 0.00, 2.00)     # (x, y, z) m
tag_pos    = (2.50, 4.00, 1.00)     # (x, y, z) m

# ===== 2. 測量設定 =====
ROUNDS = 10
PORT   = '/dev/ttyUSB0'
BAUD   = 57600

# ===== 3. 串口連線 =====
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"[Info] Connected to {PORT} @ {BAUD}bps")
except Exception as e:
    print(f"[Warning] 無法開啟串口 {PORT}: {e}")
    ser = None

# ===== 4. 讀取距離 =====
def read_distance_m(serial_iface, aid):
    """
    從串口讀取 256 bytes hex，尋找 anchor ID 後 4 bytes（小端）距離（cm）
    回傳距離（m），找不到回 0.0
    """
    if not serial_iface:
        return 0.0
    raw = serial_iface.read(256).hex()
    idx = raw.find(aid.lower())
    if idx >= 0:
        hex_dis = raw[idx+16:idx+24]
        try:
            cm = int.from_bytes(bytes.fromhex(hex_dis)[::-1], 'big')
        except ValueError:
            cm = 0
        if 0 < cm < 32768:
            return cm / 100.0
    return 0.0

# ===== 5. 主程式 =====
def main():
    # 計算真實距離（m）
    true_d = np.linalg.norm(np.array(anchor_pos) - np.array(tag_pos))

    errors = []
    for i in range(ROUNDS):
        meas_d = read_distance_m(ser, anchor_id)
        if meas_d <= 0.0:
            print(f"{i+1:04d}  讀取失敗，略過")
            continue
        err_cm = (meas_d - true_d) * 100.0
        errors.append(round(err_cm, 3))
        print(f"{i+1:04d}  error_cm={err_cm:.3f}")

    if ser:
        ser.close()

    # 輸出
    output_dir = os.path.expanduser('/home/e520/uwb_results')
    os.makedirs(output_dir, exist_ok=True)
    csv_path  = os.path.join(output_dir, 'uwb_線性線性_含估計座標.csv')
    xlsx_path = os.path.join(output_dir, 'uwb_線性_含估計座標.xlsx')

    df = pd.DataFrame({'error_cm': errors})
    df.to_csv(csv_path, index=False)
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='1D_Range_Error')

    print(f"[Info] 已儲存 CSV: {csv_path}")
    print(f"[Info] 已儲存 Excel: {xlsx_path} ({len(df)} 筆 error_cm)")

if __name__ == "__main__":
    main()
