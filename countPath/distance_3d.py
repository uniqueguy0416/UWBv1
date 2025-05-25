import serial, binascii
import numpy as np

# ———— 1. Anchor 在 EPSG:3826 下的平面座標 (m) 及高度 (m) ————
# 你要先把 Anchor 的經緯度轉到 3826，再手動加上高度 (或量測得到)
anchors = np.array([
    [0.0, 0.0, 1.5],   # Anchor6: X1, Y1, Z1
    [5.0, 0.0, 1.5],   # Anchor7: X2, Y2, Z2
    [5.0, 10.0, 1.5],   # Anchor9: X3, Y3, Z3
    [0.0, 10.0, 1.5]    #Anchor8:X4,Y4,Z4
])

anchor_IDs = ['0241000000000000','0341000000000000','0541000000000000','0441000000000000']
COM_PORT  = '/dev/ttyUSB0'
BAUD_RATE = 57600

# ———— 2. 讀 DW1000 距離函式 ————
def read_distances(ser):
    ser.flushInput()
    raw = ser.read(66 * len(anchor_IDs))
    rx  = binascii.hexlify(raw).decode()
    diss = np.zeros(3)
    for i, aid in enumerate(anchor_IDs):
        idx = rx.find(aid)
        if idx>=0:
            hex_d = rx[idx+16:idx+24][::-1]
            d = int(hex_d,16)
            if d>=32768: d = 0
            diss[i] = d/100.0   # 轉成公尺
    return diss

# ———— 3. 3D Trilateration 函式 ————
def trilaterate_3d(anchors, r):
    P1, P2, P3 = anchors
    r1, r2, r3 = r

    # 單位向量 ex
    ex = (P2 - P1)[:3]
    d  = np.linalg.norm(ex)
    ex = ex / d

    # i, ey
    P3_P1 = (P3 - P1)[:3]
    i  = np.dot(ex, P3_P1)
    temp = P3_P1 - i*ex
    ey = temp / np.linalg.norm(temp)

    # ez （垂直向量）
    ez = np.cross(ex, ey)

    # j
    j = np.dot(ey, P3_P1)

    # x, y
    x = (r1*r1 - r2*r2 + d*d) / (2*d)
    y = (r1*r1 - r3*r3 + i*i + j*j - 2*i*x) / (2*j)

    # z²
    z2 = r1*r1 - x*x - y*y
    z = np.sqrt(z2) if z2>0 else 0.0

    # 最終座標
    result = P1 + x*ex + y*ey + z*ez
    return result  # [X,Y,Z]

# ———— 4. 主流程：不斷讀距離並輸出 Tag 座標 ————
if __name__ == "__main__":
    import time
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    try:
        while True:
            dists = read_distances(ser)
            if np.any(dists==0):
                print("讀距失敗，重試…")
                time.sleep(0.2)
                continue

            tag_xyz = trilaterate_3d(anchors, dists)
            print(f"Tag 座標 (EPSG:3826 + Z)：X={tag_xyz[0]:.3f} m, "
                  f"Y={tag_xyz[1]:.3f} m, Z={tag_xyz[2]:.3f} m")
            time.sleep(0.5)

    except KeyboardInterrupt:
        ser.close()
