#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UWB Anchor-Tag TWR 量測（只輸出誤差；路徑與檔名與原檔相同）
----------------------------------------------------------------
• 單一 Anchor + 單一 Tag
• 串口讀距離（cm，小端）→ 轉 m
• 1D range error（cm）= (量測距離 - 真實距離) * 100
• 只輸出一欄：error_cm
• 輸出路徑與檔名：
  /home/e520/uwb_results/uwb_線性線性_含估計座標.csv
  /home/e520/uwb_results/uwb_線性_含估計座標.xlsx
"""

import os
import time
import serial
import numpy as np
import pandas as pd

# ===== 參數設定 =====
anchor_id  = '0241000000000000'   # 8-byte HEX（需與資料幀一致）
anchor_pos = (3.00, 0.00, 1.50)   # (x, y, z) in meters
tag_pos    = (2.50, 4.00, 1.00)   # (x, y, z) in meters

ROUNDS = 10
PORT   = '/dev/ttyUSB0'           # Windows 改 'COM3'
BAUD   = 57600

# ===== 輸出路徑與檔名（與你原本一致）=====
output_dir = os.path.expanduser('/home/e520/uwb_results')
csv_path   = os.path.join(output_dir, 'uwb_線性線性_含估計座標.csv')
xlsx_path  = os.path.join(output_dir, 'uwb_線性_含估計座標.xlsx')


# ===== 串口連線 =====
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"[Info] Connected to {PORT} @ {BAUD}bps")
except Exception as e:
    print(f"[Warning] 無法開啟串口 {PORT}: {e}")
    ser = None


# ===== 讀距離（沿用你的封包結構）=====
def read_distance_m(serial_iface, anchor_hex_id, retries=8):
    """
    在 raw hex 中尋找 8-byte Anchor ID，緊接著 4 bytes（小端）為距離(cm)。
    回傳：距離（公尺）；讀不到回 0.0
    """
    if not serial_iface:
        return 0.0

    for _ in range(retries):
        raw_hex = serial_iface.read(256).hex()
        idx = raw_hex.find(anchor_hex_id.lower())
        if idx >= 0:
            hex_dis = raw_hex[idx + 16 : idx + 24]  # ID(16 hex) 後的 8 hex
            try:
                cm = int.from_bytes(bytes.fromhex(hex_dis)[::-1], 'big')
            except ValueError:
                cm = 0
            if 0 < cm < 32768:
                return cm / 100.0  # m
        time.sleep(0.01)
    return 0.0


def main():
    os.makedirs(output_dir, exist_ok=True)

    # 真實距離（Anchor ↔ Tag）
    true_d = float(np.linalg.norm(np.array(anchor_pos) - np.array(tag_pos)))  # m

    errors = []
    saved = 0

    for i in range(ROUNDS):
        meas_d = read_distance_m(ser, anchor_id)
        if meas_d <= 0.0:
            print(f"{i+1:04d}  讀取失敗，略過")
            continue

        err_cm = (meas_d - true_d) * 100.0
        errors.append(round(err_cm, 3))
        saved += 1
        print(f"{i+1:04d}  error_cm={err_cm:.3f}")

    if ser:
        ser.close()

    # 只輸出一欄：error_cm
    df = pd.DataFrame({'error_cm': errors})

    # 寫入 CSV（與原檔名相同）
    df.to_csv(csv_path, index=False)

    # 寫入 Excel（與原檔名相同）
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='1D_Range_Error')

    print(f"[Info] 已儲存 CSV : {csv_path}")
    print(f"[Info] 已儲存 Excel: {xlsx_path}（{saved} 筆 error_cm）")


if __name__ == "__main__":
    main()
