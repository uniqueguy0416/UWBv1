import serial
import binascii
import numpy as np
import random

COM_PORT = '/dev/ttyUSB0'  # for rpi/wsl
# COM_PORT = 'COM4'   # for computer

anchor_IDs = ['0241000000000000', '0341000000000000', '0541000000000000']
BAUD_RATES = 57600

# anchor position
x0,  y0 = 25.17597860, 121.4515157  # CRS coordinate of anchor 6
x02, y02 = 25.17597860, 121.45159396   # CRS coordinate of anchor 7
x03, y03 = 25.17605788, 121.4515157    # CRS coordinate of anchor 9

# multipliers for CRS conversion
_x_multiplier = 50000  # unit:(m/longitude)
_y_multiplier = 50000  # unit:(m/latitude)
x_multiplier = 55000  # unit:(m/longitude)
y_multiplier = 55000  # unit:(m/latitude)

# relative anchor coordinates
x1, y1 = 0, 0
x2 = (x02 - x0) * _x_multiplier
y2 = (y02 - y0) * _y_multiplier
x3 = (x03 - x0) * _x_multiplier
y3 = (y03 - y0) * _y_multiplier

# helper to swap endianness in hex string
def swapEndianness(hexstring):
    ba = bytearray.fromhex(hexstring)
    ba.reverse()
    return ba.hex()

class UWBpos:
    def __init__(self):
        print("initializing UWB...")
        print(f"(anchor 7)x2={x2}, y2={y2}")
        print(f"(anchor 9)x3={x3}, y3={y3}")
        print(f"estimated anchor 6-7:{(x2**2 + y2**2)**0.5}")
        print(f"estimated anchor 6-9:{(x3**2 + y3**2)**0.5}")
        try:
            self.ser_UWB = serial.Serial(COM_PORT, BAUD_RATES)
            self.ser_success = True
            print(f"Connected to {COM_PORT}")
        except Exception as e:
            print(f"Cannot connect to {COM_PORT}. Error message: {e}")
            self.ser_success = False

        # geometry setup
        self.X = np.array([x1, x2, x3])
        self.Y = np.array([y1, y2, y3])
        self.XY = np.cross(self.X, self.Y).dot(np.array([1,1,1]))
        self.C0 = np.array([x1*x1 + y1*y1,
                            x2*x2 + y2*y2,
                            x3*x3 + y3*y3])

        # original distance array
        self.diss = np.zeros(3)
        # new arrays for RSSI and CIR
        self.rssis = np.zeros(3)
        self.cirs  = np.zeros(3)

        print("UWB initialized successfully.")
        print(f"anchor 6 coordinate:({x0}, {y0})")

    def UWB_read(self):
        """
        讀取所有 anchor 的 ToF 距離、RSSI、CIR，
        回傳三個 numpy 陣列：(diss, rssis, cirs)
        """
        # clear previous values
        self.diss.fill(0)
        self.rssis.fill(0)
        self.cirs.fill(0)

        if not self.ser_success:
            return self.diss, self.rssis, self.cirs

        self.ser_UWB.flushInput()
        raw = self.ser_UWB.read(66 * len(anchor_IDs))
        rx = binascii.hexlify(raw).decode('utf-8')

        for idx, anchor_ID in enumerate(anchor_IDs):
            pos = rx.find(anchor_ID)
            # ensure enough length for distance+RSSI+CIR
            if 0 <= pos <= len(rx) - 48:
                # parse distance (8 hex chars)
                hex_dis = rx[pos+16 : pos+24]
                val_dis = int(swapEndianness(hex_dis), 16) if hex_dis else 0
                if val_dis >= 32768:
                    val_dis = 0
                self.diss[idx] = val_dis / 100  # cm

                # parse RSSI (8 hex chars)
                hex_rssi = rx[pos+24 : pos+32]
                val_rssi = int(swapEndianness(hex_rssi), 16) if hex_rssi else 0
                self.rssis[idx] = val_rssi

                # parse CIR (16 hex chars)
                hex_cir = rx[pos+32 : pos+48]
                val_cir = int(swapEndianness(hex_cir), 16) if hex_cir else 0
                self.cirs[idx] = val_cir

                print(f"anchor[{idx}] → "
                      f"距離: {self.diss[idx]:.2f} cm, "
                      f"RSSI: {self.rssis[idx]}, "
                      f"CIR: {self.cirs[idx]}")

        return self.diss, self.rssis, self.cirs

    def fake_read(self):
        random.seed()
        self.diss[0] = 10 * random.random()
        self.diss[1] = 10 * random.random()
        self.diss[2] = 30 - self.diss[0] - self.diss[1]
        print(f"fake read: {self.diss[0]}, {self.diss[1]}, {self.diss[2]}")

    def compute_relative(self):
        r1, r2, r3 = self.diss
        C = self.C0 - np.array([r1*r1, r2*r2, r3*r3])
        CY = np.cross(C, self.Y).dot(np.array([1,1,1]))
        XC = np.cross(self.X, C).dot(np.array([1,1,1]))
        x = CY / self.XY / 2
        y = XC / self.XY / 2
        return x, y

    def compute_CRS(self):
        x, y = self.compute_relative()
        print(f"multiplier:{x_multiplier}, {y_multiplier}")
        return x0 + x/x_multiplier, y0 + y/y_multiplier

    def UWB_read_compute_CRS_5(self):
        x_sum, y_sum = 0, 0
        count = 0
        while count < 5:
            diss, _, _ = self.UWB_read()
            if 0 not in diss:
                x_rel, y_rel = self.compute_relative()
                x_sum += x_rel
                y_sum += y_rel
                count += 1
                print(count)
        x_avg = x_sum / 5
        y_avg = y_sum / 5
        print(f"multiplier:{x_multiplier}, {y_multiplier}")
        return x0 + x_avg/x_multiplier, y0 + y_avg/y_multiplier

    def recalibrate(self):
        print("hold tag close to anchor 6")
        d2_sum, d3_sum = 0, 0
        count = 0
        while count < 10:
            diss, _, _ = self.UWB_read()
            if diss[0] < 0.1:
                d2_sum += diss[1]
                d3_sum += diss[2]
                count += 1
                print(f"taking test value {count}/10...")
        d2_avg = d2_sum / 10
        d3_avg = d3_sum / 10
        x2_rel, y2_rel = x02 - x0, y02 - y0
        x3_rel, y3_rel = x03 - x0, y03 - y0
        delta = np.linalg.det([[x2_rel**2, y2_rel**2], [x3_rel**2, y3_rel**2]])
        delta_x = np.linalg.det([[d2_avg**2, y2_rel**2], [d3_avg**2, y3_rel**2]])
        delta_y = np.linalg.det([[x2_rel**2, d2_avg**2], [x3_rel**2, d3_avg**2]])
        new_x_mul = (delta_x / delta)**0.5
        new_y_mul = (delta_y / delta)**0.5
        print("recalibration completed! new multipliers:")
        print(f"x = {new_x_mul}")
        print(f"y = {new_y_mul}")
        return new_x_mul, new_y_mul

    def get_anchor_CRS(self, idx):
        if idx == '6':
            return x0, y0
        elif idx == '7':
            return x02, y02
        elif idx == '9':
            return x03, y03
        else:
            return -1, -1

# 測試程式
if __name__ == '__main__':
    try:
        uwbpos = UWBpos()
        for i in range(10):
            diss, rssis, cirs = uwbpos.UWB_read()
            print(f"anchor ID 6: {diss[0]} cm, RSSI: {rssis[0]}, CIR: {cirs[0]}")
            print(f"anchor ID 7: {diss[1]} cm, RSSI: {rssis[1]}, CIR: {cirs[1]}")
            print(f"anchor ID 9: {diss[2]} cm, RSSI: {rssis[2]}, CIR: {cirs[2]}")
            x, y = uwbpos.compute_CRS()
            print(f"(x, y) = ({x}, {y})")
    except KeyboardInterrupt:
        pass
