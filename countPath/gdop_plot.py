#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exp12_gdop_measure.py

同時執行實驗1（定位量測）與實驗2（GDOP計算），對20個測點逐一：
  • 測距並計算平均 UWB 位置
  • 計算理論 GDOP（真值點）
  • 計算實測 GDOP（量測點）
  • 計算定位誤差
並輸出 CSV 與圖檔。

使用前請先：
  1. 在相同資料夾放入 read_GIPS_distance.py（含 UWBpos 定義）
  2. 建立 points.csv：
       point_id,x_true,y_true
       P01,0.0,0.0
       P02,1.0,0.0
       …
       P20,3.5,4.0
  3. 安裝套件：
       pip3 install pyserial numpy matplotlib pandas
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from read_GIPS_distance import UWBpos

def compute_gdop(anchors: np.ndarray, x_tag: float, y_tag: float) -> float:
    """計算2D GDOP"""
    diffs = anchors - np.array([x_tag, y_tag])
    dists = np.linalg.norm(diffs, axis=1)
    G = diffs / dists[:, None]
    Q = np.linalg.inv(G.T @ G)
    return np.sqrt(np.trace(Q))

def main():
    # --- 1. 載入測點清單 ---
    df_pts = pd.read_csv('points.csv')  # point_id, x_true, y_true

    # --- 2. 初始化 UWBpos，取得 Anchor 相對座標 ---
    uwb = UWBpos()
    anchors = np.vstack((uwb.X, uwb.Y)).T   # shape (3,2)

    results = []
    # --- 3. 逐點量測 & GDOP 計算 ---
    for idx, row in df_pts.iterrows():
        pid = row['point_id']
        x_true = row['x_true']
        y_true = row['y_true']

        input(f"\n請將 Tag 放在點 {pid} (x={x_true:.2f}, y={y_true:.2f})，按 Enter 開始量測…")

        # 重複量測多次平均
        n_meas = 10
        xs, ys = [], []
        for i in range(n_meas):
            uwb.UWB_read()
            x_rel, y_rel = uwb.compute_relative()
            xs.append(x_rel)
            ys.append(y_rel)
        x_meas = np.mean(xs)
        y_meas = np.mean(ys)

        # 計算 GDOP & 誤差
        gdop_true = compute_gdop(anchors, x_true, y_true)
        gdop_meas = compute_gdop(anchors, x_meas, y_meas)
        err = np.hypot(x_meas - x_true, y_meas - y_true)

        print(f"{pid} → measured (x,y)=({x_meas:.2f},{y_meas:.2f}), "
              f"GDOP_true={gdop_true:.2f}, GDOP_meas={gdop_meas:.2f}, err={err:.2f} m")

        results.append({
            'point_id': pid,
            'x_true': x_true, 'y_true': y_true,
            'x_meas': x_meas, 'y_meas': y_meas,
            'gdop_true': gdop_true, 'gdop_meas': gdop_meas,
            'err': err
        })

    # --- 4. 寫出 CSV ---
    df_res = pd.DataFrame(results)
    df_res.to_csv('exp1_2_results.csv', index=False)
    print("\n已儲存結果：exp1_2_results.csv")

    # --- 5. 畫散佈圖：GDOP_true 上色 ---
    plt.figure(figsize=(6,5))
    sc = plt.scatter(df_res['x_true'], df_res['y_true'],
                     c=df_res['gdop_true'], cmap='viridis', s=50)
    plt.colorbar(sc, label='GDOP at True Points')
    plt.scatter(anchors[:,0], anchors[:,1],
                c='red', marker='x', label='Anchors')
    plt.legend()
    plt.xlabel('X (m) relative to Anchor6')
    plt.ylabel('Y (m) relative to Anchor6')
    plt.title('GDOP at Experiment 1 True Points')
    plt.tight_layout()
    plt.savefig('gdop_at_true_points.png')
    print("已儲存圖檔：gdop_at_true_points.png")

if __name__ == '__main__':
    main()
