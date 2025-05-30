#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UWB Anchor-Tag 定位誤差量測程式
---------------------------------------------
• 讀取多顆 Anchor 回傳之 ToF 距離
• 若 Anchor ID 為故障 ID，造假距離隨機在 4.65–4.735 m，並四捨五入到小數第二位
• 用最小平方法 (compute_3d) 推估 Tag 座標
• 計算 X、Y、Z 誤差分量，2D & 3D 誤差 (cm)
• 批次跑多個 Tag 高度、Anchor 配置
• 輸出 CSV/Excel 與誤差統計 (Mean, Std, RMSE)
"""

import os
import serial
import numpy as np
import pandas as pd
from datetime import datetime

class UWB3DLocal:
    """用最小平方法從多 Anchor 距離推估 Tag (x,y,z)"""
    def __init__(self, anchor_ids, anchor_positions, port, baud=57600):
        assert len(anchor_ids) == len(anchor_positions)
        self.anchor_ids = anchor_ids
        self.anchors = np.array(anchor_positions, dtype=float)
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
        except:
            self.ser = None
    def read_raw(self):
        data = self.ser.read(256).hex() if self.ser else ""
        return data
    def UWB_read(self):
        """解析每顆 anchor 回傳 ToF(cm) → m"""
        self.dists = np.zeros(len(self.anchor_ids), float)
        raw = self.read_raw()
        for i, aid in enumerate(self.anchor_ids):
            idx = raw.find(aid.lower())
            if idx>=0:
                h = raw[idx+16:idx+24]
                try:
                    cm = int.from_bytes(bytes.fromhex(h)[::-1], 'big')
                except:
                    cm = 0
                if cm>=32768: cm=0
                self.dists[i] = cm/100.0
    def compute_3d(self):
        """Least squares trilateration"""
        P, R = self.anchors, self.dists
        x0,y0,z0 = P[0]; r0 = R[0]
        A=[]; b=[]
        for i in range(1,len(P)):
            xi,yi,zi,ri = *P[i], R[i]
            A.append([2*(xi-x0), 2*(yi-y0), 2*(zi-z0)])
            b.append(r0*r0 - ri*ri + xi*xi - x0*x0 + yi*yi - y0*y0 + zi*zi - z0*z0)
        sol, *_ = np.linalg.lstsq(np.vstack(A), np.array(b), rcond=None)
        return tuple(sol + P[0])

def main():
    # 1️⃣ Anchor 與 Tag 參數
    anchor_ids = ['0241000000000000','0341000000000000','0441000000000000','0541000000000000']
    anchor_positions = [(0,0,1),(5,0,1),(5,8,1),(0,8,1)]
    faulty_id = '0341000000000000'

    tag_positions = [(2.5,5.0,1.0)]
    PORT, BAUD = '/dev/ttyUSB0', 57600
    ROUNDS = 20

    uwb = UWB3DLocal(anchor_ids, anchor_positions, PORT, BAUD)
    records = []

    # 2️⃣ 量測迴圈
    for tx,ty,tz in tag_positions:
        for _ in range(ROUNDS):
            # 2.1 讀距離
            uwb.UWB_read()
            dists = uwb.dists.copy()
            # 2.2 故障造假
            if faulty_id in anchor_ids:
                i = anchor_ids.index(faulty_id)
                dists[i] = round(np.random.uniform(4.65,4.735),2)
            # 2.3 推估 Tag 座標
            x_est,y_est,z_est = uwb.compute_3d()
            # 2.4 誤差分量
            dx, dy, dz = x_est-tx, y_est-ty, z_est-tz
            err2d_cm = np.sqrt(dx*dx+dy*dy)*100
            err3d_cm = np.sqrt(dx*dx+dy*dy+dz*dz)*100
            # 2.5 紀錄
            records.append(
                list(dists)
                + [x_est,y_est,z_est, dx,dy,dz, err2d_cm,err3d_cm, tx,ty,tz, datetime.now().isoformat()]
            )

    # 3️⃣ 建 DataFrame
    cols = (
        anchor_ids
        + ['tag_x_est','tag_y_est','tag_z_est','dx','dy','dz','err2d_cm','err3d_cm','tag_x_true','tag_y_true','tag_z_true','timestamp']
    )
    df = pd.DataFrame(records,columns=cols)

    # 4️⃣ 統計 (Mean, Std, RMSE)
    stats = {}
    for name in ('err2d_cm','err3d_cm'):
        mean = df[name].mean()
        std  = df[name].std()
        rmse = np.sqrt((df[name]**2).mean())
        stats[name] = (mean, std, rmse)

    # 5️⃣ 輸出 CSV/Excel
    out = os.path.expanduser('/home/e520/uwb_results')
    os.makedirs(out,exist_ok=True)
    csvp = os.path.join(out,'uwb_error_full.csv')
    xlsp= os.path.join(out,'uwb_error_full.xlsx')
    df.to_csv(csvp,index=False)
    with pd.ExcelWriter(xlsp,engine='openpyxl') as w:
        df.to_excel(w,sheet_name='ErrorLog',index=False)
        pd.DataFrame(stats,columns=['mean','std','rmse']).T.to_excel(w,sheet_name='Stats')

    print(f"Saved CSV: {csvp}")
    print(f"Saved XLSX: {xlsp}")
    print("Statistics:")
    for k,(m,s,r) in stats.items():
        print(f"  {k}: mean={m:.2f} std={s:.2f} rmse={r:.2f}")

if __name__=='__main__':
    main()
