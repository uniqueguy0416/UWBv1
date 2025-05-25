import serial, binascii, time, numpy as np

anchor_IDs = ['0241000000000000']  # 或四顆 ID 都放進來
COM_PORT  = '/dev/ttyUSB0'
BAUD_RATE = 57600

def debug_read(ser):
    data = ser.read(128)             # 先取 128 bytes
    if not data:
        return None, None

    hexstr = binascii.hexlify(data).decode()
    dist_list = []

    for aid in anchor_IDs:
        idx = hexstr.find(aid)
        if idx >= 0:
            # 假設你目前試 offset=18~26
            start = idx + 18
            end   = start + 8
            hex_d = hexstr[start:end][::-1]
            raw_d = int(hex_d, 16)
            dist = (raw_d if raw_d < 32768 else 0) / 100.0
        else:
            dist = None
        dist_list.append(dist)

    return hexstr, dist_list

if __name__ == "__main__":
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(1)
    try:
        while True:
            hexstr, dists = debug_read(ser)
            if hexstr is None:
                continue

            print("="*60)
            print("RAW HEX: ")
            print(hexstr)
            print("解析後距離: ", dists)
            time.sleep(0.5)

    except KeyboardInterrupt:
        ser.close()
