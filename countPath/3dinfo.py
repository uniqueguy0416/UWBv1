#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UWB Anchor‑Tag誤差量測程式
---------------------------------------------
• 讀取多顆 Anchor 回傳的 ToF 距離
• 計算平均量測距離、理論歐幾里得距離、及誤差 (cm)
• 支援多個 Tag 位置（不同高度）批次量測
• 輸出 CSV 與 Excel，包含 Tag 真實座標與時間戳
"""

import os
import serial
import numpy as np
import pandas as pd
from datetime import datetime

# 1. 請設定：Anchor ID 與對應 xyz 座標 (m)
anchor_ids = [
    '0241000000000000',
    '0341000000000000',
    '0441000000000000',
    '0541000000000000'
]
anchor_positions = [
    (0.00, 0.00, 1.00),  # Anchor6
    (5.00, 0.00, 1.00),  # Anchor7
    (5.00, 8.00,1.00),  # Anchor8
    (0.00, 8.00,1.00)   # Anchor9
]

# 2. 請設定：Tag 實際放置座標 (x,y,z) 的列表，可多高度批次
tag_positions = [
    (2.50,  4.00, 1.00),
]

# 3. 串口與量測次數參數
PORT = '/dev/ttyUSB0'
BAUD = 57600
MEASURE_ROUNDS = 20   # 每個 Tag 位置下重複量測次數

# 4. 建立串口連線
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"[Info] Connected to {PORT} @ {BAUD}bps")
except Exception as e:
    print(f"[Warning] 無法開啟串口 {PORT}: {e}")
    ser = None

def read_distances(serial_iface, ids):
    """
    從串口讀原始 hex 資料，尋找每顆 anchor ID，
    解析出 cm 數值，轉成 m 回傳距離陣列
    """
    dists = np.zeros(len(ids), dtype=float)
    if not serial_iface:
        return dists
    raw = serial_iface.read(256).hex()
    for i, aid in enumerate(ids):
        idx = raw.find(aid.lower())
        if idx >= 0:
            hex_dis = raw[idx+16:idx+24]
            try:
                cm = int.from_bytes(bytes.fromhex(hex_dis)[::-1], 'big')
            except ValueError:
                cm = 0
            if cm >= 32768:
                cm = 0
            dists[i] = cm / 100.0
    return dists

def main():
    # 5. 建立量測結果容器
    records = []

    # 6. 依序對每個 Tag 位置做 MEASURE_ROUNDS 次量測
    for tag_pos in tag_positions:
        tx, ty, tz = tag_pos
        for _ in range(MEASURE_ROUNDS):
            # 6.1 讀取 TOF 距離
            dists = read_distances(ser, anchor_ids)
            avg_meas = dists.mean()

            # 6.2 計算每顆 Anchor 到 Tag 的理論距離，並取平均
            euclids = np.linalg.norm(np.array(anchor_positions) - np.array(tag_pos), axis=1)
            true_euclid = euclids.mean()

            # 6.3 計算誤差 (cm)
            err_cm = (avg_meas - true_euclid) * 100.0

            # 6.4 加入時間戳與紀錄
            timestamp = datetime.now().isoformat()
            records.append(
                list(dists)
                + [avg_meas, true_euclid, err_cm, tx, ty, tz, timestamp]
            )

    # 7. 整理成 DataFrame
    cols = (
        anchor_ids
        + ['avg_meas_m','true_euclid_m','error_cm','tag_x','tag_y','tag_z','timestamp']
    )
    df = pd.DataFrame(records, columns=cols)

    # 8. 輸出資料夾與檔名設定
    output_dir = os.path.expanduser("/home/e520/uwb_results")
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "uwb_error_log.csv")
    xlsx_path = os.path.join(output_dir, "uwb_error_log.xlsx")

    # 9. 儲存 CSV & Excel
    df.to_csv(csv_path, index=False)
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="ErrorLog")

    print(f"[Info] 已儲存 CSV: {csv_path}")
    print(f"[Info] 已儲存 Excel: {xlsx_path} (共 {len(df)} 筆紀錄)")

if __name__ == "__main__":
    main()
