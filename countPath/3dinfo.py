#!/usr/bin/env python3
import os
import serial
import numpy as np
import pandas as pd

class UWB3DLocal:
    def __init__(self, anchor_ids, anchor_positions,
                 port='/dev/ttyUSB0', baud=57600):
        """
        anchor_ids:      list of anchor IDs, e.g. ['0241…','0341…','0441…','0541…']
        anchor_positions:list of (x,y,z) tuples in meters, same order as anchor_ids
        """
        assert len(anchor_ids) == len(anchor_positions), \
            "ID 與座標數量必須相同"
        self.anchor_ids = anchor_ids
        self.anchors = np.array(anchor_positions, dtype=float)  # shape (m,3)
        self.dists   = np.zeros(len(anchor_ids), dtype=float)   # measured distances (m)
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
            print(f"Connected to {port} @ {baud}bps")
        except Exception as e:
            print(f"[Warning] Cannot open serial port {port}: {e}")
            self.ser = None

    def UWB_read(self):
        """Read one round of ToF distances for all anchors into self.dists"""
        if not self.ser:
            self.dists[:] = 0.0
            return
        raw = self.ser.read(200).hex()
        for i, aid in enumerate(self.anchor_ids):
            idx = raw.find(aid)
            if idx >= 0:
                hex_dis = raw[idx+16:idx+24]
                try:
                    cm = int.from_bytes(bytes.fromhex(hex_dis)[::-1], 'big')
                except ValueError:
                    cm = 0
                if cm >= 32768:
                    cm = 0
                self.dists[i] = cm / 100.0  # convert cm → m

    def compute_3d(self):
        """Compute (x, y, z) of the tag via least squares from ≥4 anchors"""
        P = self.anchors      # shape (m,3)
        R = self.dists        # shape (m,)
        x0, y0, z0 = P[0]
        r0 = R[0]
        A, b = [], []
        for i in range(1, len(P)):
            xi, yi, zi = P[i]
            ri = R[i]
            A.append([2*(xi - x0), 2*(yi - y0), 2*(zi - z0)])
            b.append((r0**2 - ri**2)
                   + (xi**2 - x0**2)
                   + (yi**2 - y0**2)
                   + (zi**2 - z0**2))
        A = np.vstack(A)
        b = np.array(b)
        sol, *_ = np.linalg.lstsq(A, b, rcond=None)
        # if P[0] is treated as origin, sol is global; otherwise add back P[0]
        return tuple(sol + P[0])

def main():
    # 1. 定義錨點 ID 及 xyz 座標 (m)
    anchor_IDs = [
        '0241000000000000',
        '0341000000000000',
        '0441000000000000',
        '0541000000000000'
    ]
    anchor_positions = [
        (0.00,  0.00, 1.00),  # anchor6 (origin)
        (5.00,  0.00, 1.00),  # anchor7
        (5.00, 10.00, 1.00),  # anchor8
        (0.00, 10.00, 1.00)   # anchor9
    ]

    # 2. 初始化 UWB3DLocal
    uwb = UWB3DLocal(anchor_IDs, anchor_positions,
                     port='/dev/ttyUSB0', baud=57600)

    # 3. 執行 N 次量測
    N = 10
    measurements = []
    for _ in range(N):
        uwb.UWB_read()
        x, y, z = uwb.compute_3d()
        # 記錄每次四顆 anchor 距離與計算出的 tag 座標
        measurements.append(list(uwb.dists) + [x, y, z])

    # 4. 準備輸出路徑
    output_dir = "/home/e520/uwb_results"
    os.makedirs(output_dir, exist_ok=True)
    csv_path   = os.path.join(output_dir, "uwb_datav2.csv")
    excel_path = os.path.join(output_dir, "UWB_3dv1.xlsx")

    # 5. 建立 DataFrame
    cols = anchor_IDs + ['tag_x', 'tag_y', 'tag_z']
    df_new = pd.DataFrame(measurements, columns=cols)

    # 6. 輸出 CSV（覆寫）
    df_new.to_csv(csv_path, index=False)
    print(f"CSV saved to {csv_path}")

    # 7. 合併舊有 Excel 資料（如果存在），去重後產生 df_all
    if os.path.exists(excel_path):
        df_old = pd.read_excel(excel_path)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
        df_all.drop_duplicates(inplace=True)
    else:
        df_all = df_new

    # 8. 計算 Summary：平均測量值、平均 Tag 座標
    avg_measured = df_all[anchor_IDs].mean()  # 每顆 anchor 平均距離
    avg_tag      = df_all[['tag_x','tag_y','tag_z']].mean().values
    # 3D Euclidean 距離 & 誤差（average measured – euclid）
    euclid = np.sqrt(((uwb.anchors - avg_tag)**2).sum(axis=1))
    error  = avg_measured.values - euclid

    df_summary = pd.DataFrame({
        'anchor_id':     anchor_IDs,
        'avg_measured_m': avg_measured.values,
        'euclid_dist_m':  euclid,
        'error_m':        error
    })

    # 9. 寫入 Excel：Measurements 與 Summary 兩個工作表
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_all.to_excel(writer, sheet_name='Measurements', index=False)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)

    print(f"Excel saved to {excel_path} with {len(df_all)} rows and summary.")

if __name__ == '__main__':
    main()
