import os
import time
import csv
import serial
import numpy as np

# ===== 參數設定 =====
anchor_id  = '0241000000000000'      # 8-byte HEX（需與資料幀一致）
anchor_pos = (3.00, 0.00, 1.50)      # (x, y, z) in meters
tag_pos    = (2.50, 4.00, 1.00)      # (x, y, z) in meters

ROUNDS = 20
PORT   = '/dev/ttyUSB0'              # Windows 可改 'COM3'
BAUD   = 57600

output_dir = os.path.expanduser('/home/e520/uwb_results')
csv_name   = 'uwb_twr_error_only.csv'


# ===== 串口連線 =====
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"[Info] Connected to {PORT} @ {BAUD}bps")
except Exception as e:
    print(f"[Warning] 無法開啟串口 {PORT}: {e}")
    ser = None



def read_distance_m(serial_iface, anchor_hex_id, retries=8):
    """
    在 raw hex 中尋找 8-byte Anchor ID，緊接著 4 bytes（小端）為距離(cm)。
    回傳：距離（公尺）；讀不到回 0.0
    """
    if not serial_iface:
        return 0.0

    for _ in range(retries):
        raw_hex = serial_iface.read(256).hex()
        idx = raw_hex.find(anchor_hex_id.lower())
        if idx >= 0:
            hex_dis = raw_hex[idx + 16 : idx + 24]  # ID(16 hex) 後的 8 hex
            try:
                cm = int.from_bytes(bytes.fromhex(hex_dis)[::-1], 'big')
            except ValueError:
                cm = 0
            if 0 < cm < 32768:
                return cm / 100.0  # m
        time.sleep(0.01)
    return 0.0


def main():
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, csv_name)

    true_d = float(np.linalg.norm(np.array(anchor_pos) - np.array(tag_pos)))  # m

    saved = 0
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['error_cm'])  

        for i in range(ROUNDS):
            meas_d = read_distance_m(ser, anchor_id)
            if meas_d <= 0.0:
                print(f"{i+1:04d}  讀取失敗，略過")
                continue

            err_cm = (meas_d - true_d) * 100.0
            w.writerow([f"{err_cm:.3f}"])
            saved += 1
            print(f"{i+1:04d}  error_cm={err_cm:.3f}")

    if ser:
        ser.close()

    print(f"[Info] 已儲存 CSV: {csv_path}（{saved} 筆 error_cm）")


if __name__ == "__main__":
    main()
