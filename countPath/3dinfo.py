#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UWB Anchor-Tag 定位誤差量測程式
---------------------------------------------
• 讀取多顆 Anchor 回傳之 ToF 距離
• 故障 Anchor 造假距離 (4.65–4.735 m) 並取小數 2 位
• 用最小平方法推估 Tag 座標
• 計算 X, Y, Z 誤差分量，2D & 3D 誤差 (cm)
• 只測單一 Tag 高度 (2.5,5.0,1.0)，重複 5 次
• 輸出 CSV/Excel 並附 Mean/Std/RMSE 統計
"""

import os
import serial
import numpy as np
import pandas as pd
from datetime import datetime

class UWB3DLocal:
    """Least squares trilateration from multiple anchors."""
    def __init__(self, ids, positions, port, baud=57600):
        assert len(ids)==len(positions)
        self.ids = ids
        self.anchors = np.array(positions, float)
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
        except:
            self.ser = None
    def read_raw(self):
        return self.ser.read(256).hex() if self.ser else ""
    def UWB_read(self):
        self.dists = np.zeros(len(self.ids),float)
        raw = self.read_raw()
        for i, aid in enumerate(self.ids):
            idx = raw.find(aid.lower())
            if idx>=0:
                h = raw[idx+16:idx+24]
                try:
                    cm = int.from_bytes(bytes.fromhex(h)[::-1],'big')
                except:
                    cm=0
                if cm>=32768: cm=0
                self.dists[i] = cm/100.0
    def compute_3d(self):
        P,R = self.anchors, self.dists
        x0,y0,z0 = P[0]; r0=R[0]
        A=[]; b=[]
        for i in range(1,len(P)):
            xi,yi,zi = P[i]; ri=R[i]
            A.append([2*(xi-x0),2*(yi-y0),2*(zi-z0)])
            b.append(r0*r0 - ri*ri + xi*xi - x0*x0 + yi*yi - y0*y0 + zi*zi - z0*z0)
        sol, *_ = np.linalg.lstsq(np.vstack(A),np.array(b),rcond=None)
        return tuple(sol + P[0])

def main():
    # 1️⃣ Anchor 設定
    anchor_ids = ['0241000000000000','0341000000000000','0441000000000000','0541000000000000']
    anchor_positions = [(0,0,1),(5,0,1),(5,8,1),(0,8,1)]
    faulty = '0341000000000000'

    # 2️⃣ 只用單一 Tag 位置，重複量測 5 次
    tag_pos = (2.5,5.0,1.0)
    ROUNDS = 5

    PORT, BAUD = '/dev/ttyUSB0', 57600
    uwb = UWB3DLocal(anchor_ids, anchor_positions, PORT, BAUD)

    records=[]
    tx,ty,tz = tag_pos
    for _ in range(ROUNDS):
        # 距離讀取
        uwb.UWB_read()
        d = uwb.dists.copy()
        # 故障造假
        if faulty in anchor_ids:
            i = anchor_ids.index(faulty)
            d[i] = round(np.random.uniform(4.65,4.735),2)
        # Trilateration
        x_est,y_est,z_est = uwb.compute_3d()
        # 誤差分量
        dx,dy,dz = x_est-tx, y_est-ty, z_est-tz
        err2d = np.sqrt(dx*dx+dy*dy)*100
        err3d = np.sqrt(dx*dx+dy*dy+dz*dz)*100
        # 紀錄
        records.append(
            list(d)
            + [x_est,y_est,z_est, dx,dy,dz, err2d,err3d, tx,ty,tz, datetime.now().isoformat()]
        )

    # 3️⃣ DataFrame + 統計
    cols = (
      anchor_ids
      + ['x_est','y_est','z_est','dx','dy','dz','err2d_cm','err3d_cm','x_true','y_true','z_true','ts']
    )
    df = pd.DataFrame(records,columns=cols)

    stats={}
    for c in ('err2d_cm','err3d_cm'):
        m=df[c].mean(); s=df[c].std(); r=np.sqrt((df[c]**2).mean())
        stats[c]=(m,s,r)

    # 4️⃣ 輸出
    out=os.path.expanduser('/home/e520/uwb_results')
    os.makedirs(out,exist_ok=True)
    csvf=os.path.join(out,'uwb_5shot.csv')
    xlsf=os.path.join(out,'uwb_5shot.xlsx')
    df.to_csv(csvf,index=False)
    with pd.ExcelWriter(xlsf,engine='openpyxl') as w:
        df.to_excel(w,sheet_name='Log',index=False)
        pd.DataFrame(stats,columns=['mean','std','rmse']).T.to_excel(w,'Stats')

    print("Saved:",csvf,xlsf)
    for k,(m,s,r) in stats.items():
        print(f"{k}: mean={m:.2f},std={s:.2f},rmse={r:.2f}")

if __name__=='__main__':
    main()
