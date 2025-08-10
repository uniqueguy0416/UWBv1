#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UWB Anchor-Tag 1D Range Error 量測程式（全假資料版，誤差控制在 ±2–4 cm）
-----------------------------------------------------------------------
• 多錨點結構與 least_squares 保留
• 不連接串口，所有 anchor 距離皆用隨機生成
• 每回合每個 anchor 的誤差（cm）為隨機 ±2–4 cm
• 輸出 CSV/Excel 格式與原版相同
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime
from scipy.optimize import least_squares
import random

# 1. Anchor ID 與對應標籤、位置 (x, y, z)
anchor_ids = [
    '0241000000000000',  # Anchor6
    '0341000000000000',  # Anchor7 
    '0441000000000000',  # Anchor8
    '0541000000000000'   # Anchor9
]
anchor_labels = ['anchor6', 'anchor7', 'anchor8', 'anchor9']
anchor_positions = [
    (4.00, 0.00, 2.00),
    (4.00, 2.00, 0.00),
    (5.00, 8.00, 2.00),
    (0.00, 6.00, 1.5)
]

# 2. Tag 真實放置座標
tag_pos = (2.5, 4.0, 1.0)

# 3. 量測次數
ROUNDS = 10
ERROR_MIN = 2.0  # cm
ERROR_MAX = 4.0  # cm

# ---- 生成假距離 ----
def generate_fake_distances(anchor_positions, tag_pos, err_min_cm, err_max_cm):
    """
    根據真實距離 + 指定誤差範圍（cm）生成假量測距離（m）
    誤差隨機正負，並控制在 err_min_cm ~ err_max_cm
    """
    true_dists = np.linalg.norm(np.array(anchor_positions) - np.array(tag_pos), axis=1)
    fake_dists = []
    for td in true_dists:
        err_cm = random.uniform(err_min_cm, err_max_cm)
        if random.random() < 0.5:
            err_cm *= -1  # 隨機正負
        fake_d = td + (err_cm / 100.0)  # cm -> m
        fake_dists.append(round(fake_d, 3))
    return np.array(fake_dists)

# ---- least_squares 定位 ----
def estimate_tag_position(anchor_positions, measured_dists, initial_guess=None):
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

# ---- 主程式 ----
def main():
    records = []
    tx, ty, tz = tag_pos

    for _ in range(ROUNDS):
        # 用假資料生成距離
        dists = generate_fake_distances(anchor_positions, tag_pos, ERROR_MIN, ERROR_MAX)

        # 計算平均量測距離
        avg_meas = dists.mean()

        # 計算真實距離平均
        true_ds = np.linalg.norm(np.array(anchor_positions) - np.array(tag_pos), axis=1)
        avg_true = true_ds.mean()

        # 計算 1D range error（cm）
        err_cm = (avg_meas - avg_true) * 100.0

        # 估計 Tag 座標
        est_x, est_y, est_z = estimate_tag_position(anchor_positions, dists)

        # 時間戳
        timestamp = datetime.now().isoformat()

        records.append(
            list(dists)
            + [avg_meas, avg_true, err_cm]
            + [tx, ty, tz]
            + [est_x, est_y, est_z]
            + [timestamp]
        )

    # 輸出 DataFrame
    cols = (
        anchor_labels
        + ['avg_meas_m', 'avg_true_m', 'error_cm']
        + ['tag_x_true', 'tag_y_true', 'tag_z_true']
        + ['tag_x_est', 'tag_y_est', 'tag_z_est']
        + ['timestamp']
    )
    df = pd.DataFrame(records, columns=cols)

    # 輸出
    output_dir = os.path.expanduser('/home/e520/uwb_results')
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, 'uwb_tt_含估計座標.csv')
    xlsx_path = os.path.join(output_dir, 'uwb_tt_含估計座標.xlsx')

    df.to_csv(csv_path, index=False)
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='1D_Range_Error')

    print(f"[Info] 已儲存 CSV: {csv_path}")
    print(f"[Info] 已儲存 Excel: {xlsx_path} ({len(df)} 筆紀錄)")
    print(df[['error_cm']])

if __name__ == "__main__":
    main()
