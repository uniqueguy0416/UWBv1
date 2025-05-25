import serial, binascii
import numpy as np
import time

# 只用一顆 Anchor
anchor_IDs = ['0241000000000000']
COM_PORT  = '/dev/ttyUSB0'
BAUD_RATE = 57600

def read_distance(ser):
    # 等待資料到達
    time.sleep(0.1)
    n = ser.in_waiting or 64
    raw = ser.read(n)
    rx  = binascii.hexlify(raw).decode()
    idx = rx.find(anchor_IDs[0])
    if idx>=0:
        hex_d = rx[idx+16:idx+24][::-1]
        d = int(hex_d,16)
        return (d if d<32768 else 0)/100.0
    return None

if __name__=='__main__':
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    try:
        while True:
            r = read_distance(ser)
            if r is not None:
                print(f"Anchor6–Tag 距離：{r:.2f} m")
            else:
                print("沒有偵測到距離，重試…")
    except KeyboardInterrupt:
        ser.close()
