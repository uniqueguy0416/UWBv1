import serial, binascii, time, numpy as np

# Anchor Cartesian 座標
anchors = {
    '0241000000000000': np.array([0.0,  0.0,  1.5]),
    '0341000000000000': np.array([5.0,  0.0,  1.5]),
    '0541000000000000': np.array([5.0, 10.0,  1.5]),
    '0441000000000000': np.array([0.0, 10.0,  1.5]),
}
anchor_IDs = list(anchors.keys())
COM_PORT  = '/dev/ttyUSB0'
BAUD_RATE = 57600

class UWB3D:
    def __init__(self):
        self.ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=0.1)
        time.sleep(1)  # 等模組啟動

    def read_distances(self, timeout=1.0):
        """
        持續從串口讀，直到看到所有 anchor_IDs
        或超過 timeout (秒) 為止。
        回傳 dict{aid: dist(m) or None}
        """
        end = time.time() + timeout
        buf = ""  # 累積 hex string
        distances = {aid: None for aid in anchor_IDs}
        while time.time() < end and any(v is None for v in distances.values()):
            n = self.ser.in_waiting or 1
            data = self.ser.read(n)
            if not data:
                continue
            buf += binascii.hexlify(data).decode()
            # 嘗試解析每一顆
            for aid in anchor_IDs:
                if distances[aid] is None and aid in buf:
                    idx   = buf.find(aid)
                    start = idx + 18     # ← 根據實際偏移再微調
                    hex_d = buf[start:start+8][::-1]
                    raw_d = int(hex_d, 16)
                    distances[aid] = (raw_d if raw_d < 32768 else 0) / 100.0
        return distances

    def trilaterate(self, dists):
        # 最小平方 3D Trilateration
        ids = anchor_IDs
        P1, r1 = anchors[ids[0]], dists[ids[0]]
        A, b = [], []
        x1,y1,z1 = P1
        for aid in ids[1:]:
            Pi, ri = anchors[aid], dists[aid]
            xi, yi, zi = Pi
            A.append([2*(xi-x1), 2*(yi-y1), 2*(zi-z1)])
            b.append((xi*xi+yi*yi+zi*zi - ri*ri)
                   - (x1*x1+y1*y1+z1*z1 - r1*r1))
        sol, *_ = np.linalg.lstsq(np.array(A), np.array(b), rcond=None)
        return sol  # [x,y,z]

    def run(self):
        try:
            while True:
                d = self.read_distances()
                if all(v is not None and v>0 for v in d.values()):
                    x,y,z = self.trilaterate(d)
                    print(f"Tag XYZ: X={x:.3f}, Y={y:.3f}, Z={z:.3f}")
                else:
                    print("讀距不完整，跳過…", d)
                time.sleep(0.2)
        except KeyboardInterrupt:
            self.ser.close()

if __name__ == "__main__":
    UWB3D().run()
