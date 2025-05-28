#!/usr/bin/env python3
import os
import serial
import numpy as np
import pandas as pd

class UWB3DLocal:
    def __init__(self, anchor_ids, anchor_positions, port='/dev/ttyUSB0', baud=57600):
        """
        anchor_ids:      list of anchor IDs, e.g. ['0241…','0341…','0441…','0541…']
        anchor_positions:list of (x,y,z) tuples in meters, same order as anchor_ids
        """
        assert len(anchor_ids) == len(anchor_positions), "ID 與座標數量必須相同"
        self.anchor_ids = anchor_ids
        self.anchors = np.array(anchor_positions, dtype=float)  # shape (m,3)
        self.dists   = np.zeros(len(anchor_ids), dtype=float)   # measured distances (m)
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
        except Exception:
            self.ser = None

    def UWB_read(self):
        """Read one round of distances for all anchors and fill self.dists"""
        if not self.ser:
            self.dists[:] = 0.0
            return
        raw = self.ser.read(200).hex()
        for i, aid in enumerate(self.anchor_ids):
            idx = raw.find(aid)
            if idx >= 0:
                hex_dis = raw[idx+16 : idx+24]
                try:
                    cm = int.from_bytes(bytes.fromhex(hex_dis)[::-1], 'big')
                except ValueError:
                    cm = 0
                if cm >= 32768:
                    cm = 0
                self.dists[i] = cm / 100.0

    def compute_3d(self):
        """Compute (x,y,z) by least squares from m>=4 anchors"""
        P = self.anchors
        R = self.dists
        x0,y0,z0 = P[0]; r0 = R[0]
        A, b = [], []
        for i in range(1, len(P)):
            xi, yi, zi = P[i]; ri = R[i]
            A.append([2*(xi-x0), 2*(yi-y0), 2*(zi-z0)])
            b.append((r0**2 - ri**2)
                   + (xi**2 - x0**2)
                   + (yi**2 - y0**2)
                   + (zi**2 - z0**2))
        A = np.vstack(A); b = np.array(b)
        sol, *_ = np.linalg.lstsq(A, b, rcond=None)
        return tuple(sol + P[0])

def main():
    # 1. 定義錨點
    anchor_IDs = ['0241000000000000','0341000000000000',
                  '0441000000000000','0541000000000000']
    anchor_positions = [
        (0.00,  0.00, 1.00),
        (5.00,  0.00, 1.00),
        (5.00, 10.00, 1.00),
        (0.00, 10.00, 1.00)
    ]

    uwb = UWB3DLocal(anchor_IDs, anchor_positions)
    N = 10
    results = []
    for _ in range(N):
        uwb.UWB_read()
        x,y,z = uwb.compute_3d()
        results.append(list(uwb.dists) + [x,y,z])

    # 2. 準備輸出路徑
    output_dir = "/home/e520/uwb_results"
    os.makedirs(output_dir, exist_ok=True)
    csv_path   = os.path.join(output_dir, "uwb_datav1.csv")
    excel_path = os.path.join(output_dir, "UWB3d.xlsx")

    # 3. 建立 DataFrame
    cols = anchor_IDs + ['tag_x','tag_y','tag_z']
    df_new = pd.DataFrame(results, columns=cols)

    # 4. 儲存 CSV（覆寫）
    df_new.to_csv(csv_path, index=False)
    print(f"CSV saved to {csv_path}")

    # 5. 讀取舊 Excel 並合併（如存在），否則用新資料
    if os.path.exists(excel_path):
        df_old = pd.read_excel(excel_path)
        df_all = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates()
    else:
        df_all = df_new

    # 6. 計算 summary：平均測量、平均 tag 座標
    avg_measured = df_all[anchor_IDs].mean()
    avg_tag = df_all[['tag_x','tag_y','tag_z']].mean().values
    # 3D Euclidean 距離 & 誤差
    eucl = np.sqrt(((uwb.anchors - avg_tag)**2).sum(axis=1))
    error = avg_measured.values - eucl

    df_summary = pd.DataFrame({
        'anchor_id': anchor_IDs,
        'avg_measured_m': avg_measured.values,
        'euclid_dist_m': eucl,
        'error_m': error
    })

    # 7. 寫入 Excel：Measurements 與 Summary 兩個工作表
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_all.to_excel(writer, sheet_name='Measurements', index=False)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
    print(f"Excel saved to {excel_path} with {len(df_all)} rows and summary.")

if __name__=='__main__':
    main()

