import serial
import numpy as np

class UWB3DLocal:
    def __init__(self, anchor_ids, anchor_positions, port='/dev/ttyUSB0', baud=57600):
        assert len(anchor_ids) == len(anchor_positions), "ID 與座標數量必須相同"
        self.anchor_ids = anchor_ids
        self.anchors = np.array(anchor_positions)  # shape (4,3)
        self.dists   = np.zeros(len(anchor_ids))   # 量測距離 r_i（公尺）
        self.ser = serial.Serial(port, baud, timeout=1)

    def UWB_read(self):
        raw = self.ser.read(200).hex()
        for i, aid in enumerate(self.anchor_ids):
            idx = raw.find(aid)
            if idx>=0:
                hex_dis = raw[idx+16 : idx+24]
                dis = int.from_bytes(bytes.fromhex(hex_dis)[::-1], 'big')
                self.dists[i] = (dis if dis<32768 else 0) / 100.0

    def compute_3d(self):
        P, R = self.anchors, self.dists
        A, b = [], []
        x0,y0,z0 = P[0]; r0 = R[0]
        for i in range(1, len(P)):
            xi, yi, zi = P[i]
            ri = R[i]
            A.append([2*(xi-x0), 2*(yi-y0), 2*(zi-z0)])
            b.append((r0**2 - ri**2)
                   + (xi**2 - x0**2)
                   + (yi**2 - y0**2)
                   + (zi**2 - z0**2))
        A = np.vstack(A);  b = np.array(b)
        p_rel, *_ = np.linalg.lstsq(A, b, rcond=None)
        return tuple(p_rel + P[0])

if __name__ == '__main__':
    anchor_IDs = [
        '0241000000000000',
        '0341000000000000',
        '0441000000000000',
        '0541000000000000'
    ]
    anchor_positions = [
        (0.00, 0.00, 1.0),   # anchor6
        (5.00, 0.00, 1.0),   # anchor7
        (5.00, 10.00, 1.0),  # anchor8
        (0.00, 10.00, 1.0),  # anchor9
    ]

    uwb = UWB3DLocal(anchor_IDs, anchor_positions)
    uwb.UWB_read()

    # 印出每顆 anchor 的量測距離
    for aid, dist in zip(anchor_IDs, uwb.dists):
        print(f"Anchor ID {aid}: {dist:.2f} m")

    # 計算並印出三維定位結果
    x, y, z = uwb.compute_3d()
    print(f"\n估測 Tag 座標 (m)：x={x:.3f}, y={y:.3f}, z={z:.3f}")

    results = []
    N = 10
    for _ in range(N):
        uwb.UWB_read()
        x,y,z = uwb.compute_3d()
        # 四顆錨的量測距離 + 解算出來的 Tag 座標
        results.append(list(uwb.dists) + [x, y, z])

    # 把 results 寫入 CSV
    header = anchor_IDs + ['tag_x','tag_y','tag_z']
    with open('uwb_data.csv','w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(results)
    print("已輸出 uwb_data.csv")