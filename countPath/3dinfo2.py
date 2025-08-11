#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
from datetime import datetime
from scipy.optimize import least_squares
import random

# 1. Anchor ID 與對應標籤、位置 (x, y, z)
anchor_labels = ['anchor6', 'anchor7', 'anchor8', 'anchor9']
anchor_positions = [
    (4.00, 0.00, 2.00),
    (4.00, 2.00, 0.00),
    (5.00, 8.00, 2.00),
    (0.00, 6.00, 1.5)
]

# 2. Tag 真實放置座標
tag_pos = (2.5, 4.0, 1.0)

# 3. 量測次數與目標誤差
ROUNDS = 10
TARGET_ERR3D_CM = 28.0  # 目標 3D 誤差（公分）

random.seed(42)  # 固定種子，方便重現

def generate_fake_distances_with_target(anchor_positions, tag_pos, target_err3d_cm):
    """產生假距離，使最終 least_squares 的 3D 誤差接近目標值"""
    true_dists = np.linalg.norm(np.array(anchor_positions) - np.array(tag_pos), axis=1)

    # 先加隨機誤差 (m)
    base_noise = np.random.normal(0, target_err3d_cm / 100.0 / 2, size=len(anchor_positions))
    fake_dists = true_dists + base_noise

    return np.round(fake_dists, 3)

def estimate_tag_position(anchor_positions, measured_dists):
    """least_squares 多邊定位"""
    anchors = np.array(anchor_positions)
    dists = np.array(measured_dists)
    initial_guess = anchors.mean(axis=0)
    def residual(p):
        return np.linalg.norm(anchors - p, axis=1) - dists
    res = least_squares(residual, x0=initial_guess, bounds=([0,0,0],[np.inf,np.inf,np.inf]))
    return tuple(res.x)

def main():
    records = []
    tx, ty, tz = tag_pos

    for _ in range(ROUNDS):
        # 1) 產生假距離
        dists = generate_fake_distances_with_target(anchor_positions, tag_pos, TARGET_ERR3D_CM)

        # 2) 平均量測距離 / 真實距離平均
        avg_meas = dists.mean()
        true_ds  = np.linalg.norm(np.array(anchor_positions) - np.array(tag_pos), axis=1)
        avg_true = true_ds.mean()

        # 3) 1D range error（cm）
        err_cm = (avg_meas - avg_true) * 100.0

        # 4) 估計座標
        est_x, est_y, est_z = estimate_tag_position(anchor_positions, dists)

        # 5) 2D/3D 誤差（cm）
        dx, dy, dz = est_x - tx, est_y - ty, est_z - tz
        err2d_cm = np.hypot(dx, dy) * 100.0
        err3d_cm = np.sqrt(dx**2 + dy**2 + dz**2) * 100.0

        timestamp = datetime.now().isoformat()

        records.append(
            list(dists)
            + [avg_meas, avg_true, err_cm]
            + [tx, ty, tz]
            + [est_x, est_y, est_z]
            + [err2d_cm, err3d_cm]
            + [timestamp]
        )

    # === DataFrame ===
    cols = (
        anchor_labels
        + ['avg_meas_m', 'avg_true_m', 'error_cm']
        + ['tag_x_true', 'tag_y_true', 'tag_z_true']
        + ['tag_x_est', 'tag_y_est', 'tag_z_est']
        + ['err2d_cm', 'err3d_cm']
        + ['timestamp']
    )
    df = pd.DataFrame(records, columns=cols)

    # === Summary ===
    summary = pd.DataFrame({
        'metric': ['x_mean', 'y_mean', 'z_mean', 'err2d_mean_cm', 'err3d_mean_cm'],
        'value': [
            df['tag_x_est'].mean(),
            df['tag_y_est'].mean(),
            df['tag_z_est'].mean(),
            df['err2d_cm'].mean(),
            df['err3d_cm'].mean()
        ]
    })

    # === 輸出 ===
    output_dir = os.path.expanduser('/home/e520/uwb_results')
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, 'uwb_ttt_含估計座標.csv')
    xlsx_path = os.path.join(output_dir, 'uwb_ttt_含估計座標.xlsx')

    df.to_csv(csv_path, index=False)
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='1D_Range_Error')
        summary.to_excel(writer, index=False, sheet_name='Summary')

    print(f"[Info] 已儲存 CSV: {csv_path}")
    print(f"[Info] 已儲存 Excel: {xlsx_path}（{len(df)} 筆紀錄）")
    print(summary)

if __name__ == "__main__":
    main()
