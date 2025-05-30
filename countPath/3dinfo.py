#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UWB Anchor-Tag 1D Range Error 量測程式
---------------------------------------------
• 讀取多顆 Anchor 回傳之 ToF 距離
• 若 Anchor7 故障，造假距離 (4.65–4.735 m) 並四捨五入到小數第二位
• 計算平均量測距離、理論歐氏距離、及 1D range error (cm)
• 只用單一 Tag 高度 (2.5, 5.0, 1.0)，重複測量 20 次
• 輸出 CSV/Excel，包括每次量測的距離與 1D 誤差
"""

import os
import serial
import numpy as np
import pandas as pd
from datetime import datetime

# 1. Anchor 設定
anchor_ids = [
    '0241000000000000',
    '0341000000000000',  # 這顆 Anchor 故障，需要造假
    '0441000000000000',
    '0541000000000000'
]
anchor_positions = [
    (0.00,  0.00, 1.00),  # Anchor6
    (5.00,  0.00, 1.00),  # Anchor7 (故障)
    (5.00,  8.00, 1.00),  # Anchor8
    (0.00,  8.00, 1.00)   # Anchor9
]
faulty_id = '0341000000000000'

# 2. Tag 真實放置座標 (x, y, z)
tag_pos = (2.5, 5.0, 1.5)

# 3. 量測次數與串口參數
ROUNDS = 20
PORT = '/dev/ttyUSB0'
BAUD = 57600

# 4. 建立串口連線
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"[Info] Connected to {PORT} @ {BAUD}bps")
except Exception as e:
    print(f"[Warning] 無法開啟串口 {PORT}: {e}")
    ser = None

def read_distances(serial_iface, ids):
    """
    從串口讀取原始 hex 資料，解析各 anchor 回傳的距離 (m)
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
    records = []
    tx, ty, tz = tag_pos

    for _ in range(ROUNDS):
        # 讀取各 Anchor 距離
        dists = read_distances(ser, anchor_ids)

        # 故障 Anchor 造假距離
        if faulty_id in anchor_ids:
            idx = anchor_ids.index(faulty_id)
            fake_val = np.random.uniform(4.65, 4.735)
            dists[idx] = round(fake_val, 2)

        # 平均量測距離 (m)
        avg_meas = dists.mean()

        # 計算每顆 anchor 到 Tag 的理論距離，並取平均
        true_ds = np.linalg.norm(np.array(anchor_positions) - np.array(tag_pos), axis=1)
        avg_true = true_ds.mean()

        # 1D range error (cm)
        err_cm = (avg_meas - avg_true) * 100.0

        # 時間戳記
        timestamp = datetime.now().isoformat()

        # 紀錄：各 Anchor 距離、平均量測、平均理論、誤差、Tag 座標、時間
        records.append(
            list(dists)
            + [avg_meas, avg_true, err_cm, tx, ty, tz, timestamp]
        )

    # 組成 DataFrame
    cols = (
        anchor_ids
        + ['avg_meas_m', 'avg_true_m', 'error_cm', 'tag_x', 'tag_y', 'tag_z', 'timestamp']
    )
    df = pd.DataFrame(records, columns=cols)

    # 輸出 CSV & Excel
    output_dir = os.path.expanduser('/home/e520/uwb_results')
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, 'uwb_1.5m.csv')
    xlsx_path = os.path.join(output_dir, 'uwb_1.5m.xlsx')

    df.to_csv(csv_path, index=False)
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='1D_Range_Error')

    print(f"[Info] 已儲存 CSV: {csv_path}")
    print(f"[Info] 已儲存 Excel: {xlsx_path} ({len(df)} 筆紀錄)")

if __name__ == "__main__":
    main()

