import serial, binascii
import numpy as np
import time

# ———— 1. 定義 Anchor 的 Cartesian 座標 (m) ————
anchors = {
    '0241000000000000': np.array([0.0,  0.0,  1.5]),   # Anchor6
    '0341000000000000': np.array([5.0,  0.0,  1.5]),   # Anchor7
    '0541000000000000': np.array([5.0, 10.0,  1.5]),   # Anchor9
    '0441000000000000': np.array([0.0, 10.0,  1.5]),   # Anchor8
}

anchor_IDs = list(anchors.keys())
COM_PORT   = '/dev/ttyUSB0'
BAUD_RATE  = 57600

# ———— 2. 讀距離函式 —— 依據 raw hex dump 找到正確 offset —— 
def read_distances(ser):
    raw = ser.read(128)  # 根據實際封包長度調整
    rx  = binascii.hexlify(raw).decode()
    dists = {}
    for aid in anchor_IDs:
        idx = rx.find(aid)
        if idx >= 0:
            # 假設距離欄位在 aid 後 18~26 的 hex
            start = idx + 18
            hex_d = rx[start:start+8][::-1]
            val   = int(hex_d, 16)
            dists[aid] = (val if val < 32768 else 0) / 100.0
        else:
            dists[aid] = None
    return dists

# ———— 3. 最小平方 3D Trilateration ————
def trilaterate_3d_ls(anchors, dists):
    ids = list(anchors.keys())
    P1, r1 = anchors[ids[0]], dists[ids[0]]
    A, b = [], []
    x1,y1,z1 = P1
    for aid in ids[1:]:
        Pi = anchors[aid]; ri = dists[aid]
        xi, yi, zi = Pi
        A.append([2*(xi-x1), 2*(yi-y1), 2*(zi-z1)])
        b.append((xi*xi+yi*yi+zi*zi - ri*ri)
               - (x1*x1+y1*y1+z1*z1 - r1*r1))
    sol, *_ = np.linalg.lstsq(np.array(A), np.array(b), rcond=None)
    return sol  # 回傳 np.array([x,y,z])

# ———— 4. 主流程，不斷輸出三維座標 ————
if __name__ == "__main__":
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(1)  # 等模組穩定
    try:
        while True:
            dists = read_distances(ser)
            # 檢查是否都有值
            if all(d is not None and d>0 for d in dists.values()):
                x,y,z = trilaterate_3d_ls(anchors, dists)
                print(f"Tag XYZ: X={x:.3f} m, Y={y:.3f} m, Z={z:.3f} m")
            else:
                print("讀距不完整，跳過…", dists)
            time.sleep(0.5)
    except KeyboardInterrupt:
        ser.close()
