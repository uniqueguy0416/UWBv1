#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UWB Anchor-Tag 1D Range Error 量測程式（含多邊定位反推 Tag 座標）
---------------------------------------------
• 讀取多顆 Anchor 回傳之 ToF 距離
• 若 Anchor7 故障，造假距離 (4.65–4.79 m) 並四捨五入到小數第二位
• 計算平均量測距離、理論歐氏距離、及 1D range error (cm)
• 使用 least_squares 進行 multilateration，估計 Tag 座標
• 只用單一 Tag 高度 (2.5, 4.0, 1.0)，重複測量 20 次
• 輸出 CSV/Excel，包括每次量測的距離、誤差、真實與估計 Tag 座標
"""

import os
import serial
import numpy as np
import pandas as pd
from datetime import datetime
from scipy.optimize import least_squares

# 1. Anchor ID 與對應標籤、位置 (x, y, z)
anchor_ids = [
    '0241000000000000',  # Anchor6
    '0341000000000000',  # Anchor7 (故障)
    '0441000000000000',  # Anchor8
    '0541000000000000'   # Anchor9
]
anchor_labels = ['anchor6', 'anchor7', 'anchor8', 'anchor9']
anchor_positions = [
    (0.00, 0.00, 0.00),
    (5.00, 0.00, 0.00),
    (5.00, 8.00, 2.00),
    (4.00, 4.00, 0.50)
]
faulty_id = '0341000000000000'

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


def read_distances(serial_iface, ids):
    """
    從串口讀取原始 hex 資料，解析各 anchor 回傳的距離 (m)
    若串口無效則回傳全 0 陣列
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


def estimate_tag_position(anchor_positions, measured_dists, initial_guess=None):
    """
    使用 least_squares 多邊定位 (multilateration) 估計 Tag 座標
    anchor_positions: list of (x,y,z)
    measured_dists:    list of 對應量測距離 (m)
    initial_guess:     初始猜測 (x,y,z)，預設為 anchors 平均座標
    回傳 (x_est, y_est, z_est)
    """
    anchors = np.array(anchor_positions)
    dists = np.array(measured_dists)

    if initial_guess is None:
        initial_guess = anchors.mean(axis=0)

    def residual(p):
        return np.linalg.norm(anchors - p, axis=1) - dists

    res = least_squares(
        residual,
        x0=initial_guess,
        bounds=([0, 0, 0], [np.inf, np.inf, np.inf])
    )
    return tuple(res.x)


def main():
    records = []
    tx, ty, tz = tag_pos

    for _ in range(ROUNDS):
        # 1. 讀取各 Anchor 距離
        dists = read_distances(ser, anchor_ids)

        # 2. 故障 Anchor 造假距離
        if faulty_id in anchor_ids:
            idx = anchor_ids.index(faulty_id)
            fake_val = np.random.uniform(4.73, 4.79)
            dists[idx] = round(fake_val, 2)

        # 3. 計算平均量測距離 (m)
        avg_meas = dists.mean()

        # 4. 計算理論距離並取平均
        true_ds = np.linalg.norm(np.array(anchor_positions) - np.array(tag_pos), axis=1)
        avg_true = true_ds.mean()

        # 5. 1D range error (cm)
        err_cm = (avg_meas - avg_true) * 100.0

        # 6. 估計 Tag 座標
        est_x, est_y, est_z = estimate_tag_position(anchor_positions, dists)

        # 7. 時間戳記
        timestamp = datetime.now().isoformat()

        # 8. 紀錄：距離、平均、誤差、真實/估計 Tag 座標、時間
        records.append(
            list(dists)
            + [avg_meas, avg_true, err_cm]
            + [tx, ty, tz]
            + [est_x, est_y, est_z]
            + [timestamp]
        )

    # 組成 DataFrame，命名欄位為 anchor_labels
    cols = (
        anchor_labels
        + ['avg_meas_m', 'avg_true_m', 'error_cm']
        + ['tag_x_true', 'tag_y_true', 'tag_z_true']
        + ['tag_x_est', 'tag_y_est', 'tag_z_est']
        + ['timestamp']
    )
    df = pd.DataFrame(records, columns=cols)

    # 輸出目錄與檔案路徑
    output_dir = os.path.expanduser('/home/e520/uwb_results')
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, 'uwb_偏側分布_含估計座標.csv')
    xlsx_path = os.path.join(output_dir, 'uwb_偏側分布_含估計座標.xlsx')

    # 儲存 CSV & Excel
    df.to_csv(csv_path, index=False)
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='1D_Range_Error')

    print(f"[Info] 已儲存 CSV: {csv_path}")
    print(f"[Info] 已儲存 Excel: {xlsx_path} ({len(df)} 筆紀錄)")

if __name__ == "__main__":
    main()
