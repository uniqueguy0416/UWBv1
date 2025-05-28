import serial
import numpy as np

class UWB3DLocal:
    def __init__(self, anchor_ids, anchor_positions, port='/dev/ttyUSB0', baud=57600):
        """
        anchor_ids:      ['0241…','0341…','0441…','0541…']
        anchor_positions:[(x0,y0,z0),(x1,y1,z1),(x2,y2,z2),(x3,y3,z3)] 單位 m
        """
        assert len(anchor_ids) == len(anchor_positions), "ID 與座標數量必須相同"
        self.anchor_ids = anchor_ids
        self.anchors = np.array(anchor_positions)  # shape (4,3)
        self.dists   = np.zeros(len(anchor_ids))   # 量測距離 r_i（公尺）
        # 初始化 Serial
        self.ser = serial.Serial(port, baud, timeout=1)

    def UWB_read(self):
        """讀一輪所有 anchor 距離，填 self.dists"""
        raw = self.ser.read(200).hex()
        for i, aid in enumerate(self.anchor_ids):
            idx = raw.find(aid)
            if idx>=0:
                # 依照你原本的位址取出 ToF hex，再轉成公尺
                hex_dis = raw[idx+16 : idx+24]
                dis = int.from_bytes(bytes.fromhex(hex_dis)[::-1], 'big')
                # 大於某值視為失敗可設為 0
                self.dists[i] = (dis if dis<32768 else 0) / 100.0

    def compute_3d(self):
        """用最小平方法從 m 顆錨計算 (x,y,z)"""
        P = self.anchors      # shape (m,3)
        R = self.dists        # shape (m,)
        # 以第 0 顆當參考，建立 m-1 條線性方程
        A, b = [], []
        x0,y0,z0 = P[0]; r0 = R[0]
        for i in range(1, len(P)):
            xi, yi, zi, ri = *P[i], R[i]
            A.append([2*(xi-x0), 2*(yi-y0), 2*(zi-z0)])
            b.append((r0**2 - ri**2)
                   + (xi**2 - x0**2)
                   + (yi**2 - y0**2)
                   + (zi**2 - z0**2))
        A = np.vstack(A)
        b = np.array(b)
        p_rel, *_ = np.linalg.lstsq(A, b, rcond=None)
        # 如果第 0 顆作原點，p_rel 就是全域座標；否則要加回 P[0]
        return tuple(p_rel + P[0])

if __name__ == '__main__':
    # 先把四顆錨的 ID、實驗室量測的 xyz 座標填進來
    anchor_IDs = [
        '0241000000000000',
        '0341000000000000',
        '0441000000000000',
        '0541000000000000'
    ]
    anchor_positions = [
        (0.00, 0.00, 1.0),   # anchor6
        (5.00, 0.00, 1.0),   # anchor7
        (5.00, 10.00, 1.0),   # anchor8
        (0.00, 10.00, 1.0),   # anchor9
    ]

    uwb = UWB3DLocal(anchor_IDs, anchor_positions)
    uwb.UWB_read()
    x,y,z = uwb.compute_3d()
    print(f"估測 Tag 座標 (m)：x={x:.3f}, y={y:.3f}, z={z:.3f}")
