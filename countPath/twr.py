#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UWB Anchor-Tag 1D TWR 誤差量測（單一 Anchor；僅輸出 error_cm）
--------------------------------------------------------------
• 單一 Anchor + 單一 Tag
• 串口讀距離（cm，小端）→ 轉 m
• 每回合取 N_SAMPLES 筆，使用中位數＋MAD 剔除離群值
• 支援線性校正 d_corr = a*d_raw + b（a 為比例、b 為偏移，單位公尺）
• 只輸出一欄：error_cm（cm）（量測校正後距離 − 真實距離）
• 輸出路徑與檔名沿用你的原檔：
  /home/e520/uwb_results/uwb_線性線性_含估計座標.csv
  /home/e520/uwb_results/uwb_線性_含估計座標.xlsx
"""

import os
import time
import csv
import serial
import numpy as np

# 嘗試載入 pandas 與 openpyxl，若失敗則走回退
try:
    import pandas as pd
    HAS_PANDAS = True
except Exception:
    HAS_PANDAS = False

try:
    from openpyxl import Workbook
    HAS_OPENPYXL = True
except Exception:
    HAS_OPENPYXL = False


# ===== 1) Anchor / Tag 參數（單一 Anchor）=====
anchor_ids = [
    '0241000000000000',  # Anchor6（8-byte HEX，需與封包相符）
]
anchor_labels = ['anchor6']
anchor_positions = [
    (4.00, 0.00, 2.0),  # (x, y, z) in meters
]

# Tag 真實放置座標（用來算真值距離）
tag_pos = (2.5, 4.0, 1.0)

# ===== 2) 測量與校正參數 =====
ROUNDS     = 10           # 回合數（每回合會再連續取樣 N_SAMPLES）
N_SAMPLES  = 50           # 每回合取樣數，做中位數與離群剔除
CAL_A      = 1.000        # 線性比例校正（做完兩點校正後填入）
CAL_B      = 0.000        # 固定偏移（單位：公尺；做完校正後填入）

# 串口參數
PORT = '/dev/ttyUSB0'     # Windows 可改 'COM3'
BAUD = 57600

# 輸出（沿用你的檔名）
output_dir = os.path.expanduser('/home/e520/uwb_results')
csv_path   = os.path.join(output_dir, 'uwb_線性線性_含估計座標.csv')
xlsx_path  = os.path.join(output_dir, 'uwb_線性_含估計座標.xlsx')


# ===== 3) 串口連線 =====
try:
    ser = serial.Serial(PORT, BAUD, timeout=0.2)
    print(f"[Info] Connected to {PORT} @ {BAUD}bps")
except Exception as e:
    print(f"[Warning] 無法開啟串口 {PORT}: {e}")
    ser = None


# ===== 4) 讀距離（沿用你的封包結構）=====
def read_distance_one(serial_iface, aid, read_len=1024, retries=40, sleep_s=0.005):
    """
    讀單一 Anchor 距離（公尺）
    - 在 raw hex 中尋找 8-byte Anchor ID 後 4 bytes（小端）距離(cm)
    - 加大讀取長度與重試次數，提高成功率
    """
    if not serial_iface:
        return 0.0
    aid_hex = aid.lower()
    for _ in range(retries):
        raw = serial_iface.read(read_len)
        if not raw:
            time.sleep(sleep_s)
            continue
        raw_hex = raw.hex()
        idx = raw_hex.find(aid_hex)
        if idx >= 0:
            # ID (16 hex) 之後 8 hex 作為距離（cm，小端）
            hex_dis = raw_hex[idx + 16: idx + 24]
            try:
                cm = int.from_bytes(bytes.fromhex(hex_dis)[::-1], 'big')
            except ValueError:
                cm = 0
            if 0 < cm < 32768:
                return cm / 100.0  # 轉公尺
        time.sleep(sleep_s)
    return 0.0


def robust_median_filter(values):
    """
    使用中位數 + MAD 剔除離群值後，回傳中位數（公尺）
    """
    vals = np.array(values, dtype=float)
    # 粗略防呆：剔除非正與過大值
    vals = vals[(vals > 0) & (vals < 100)]
    if len(vals) == 0:
        return 0.0
    med = np.median(vals)
    mad = np.median(np.abs(vals - med)) + 1e-12
    # 3*MAD 規則，1.4826 為使 MAD 對應常態分佈的尺度因子
    keep = np.abs(vals - med) <= (3.0 * 1.4826 * mad)
    kept = vals[keep]
    return float(np.median(kept)) if len(kept) else float(med)


# ===== 5) 主流程 =====
def main():
    os.makedirs(output_dir, exist_ok=True)

    # 真實距離（單一 Anchor 與 Tag）
    true_d = float(np.linalg.norm(np.array(anchor_positions[0]) - np.array(tag_pos)))
    print(f"[Info] True distance = {true_d:.3f} m")

    errors = []
    saved  = 0

    for i in range(ROUNDS):
        batch = []
        # 連續取樣 N_SAMPLES
        for _ in range(N_SAMPLES):
            d = read_distance_one(ser, anchor_ids[0])
            if d > 0:
                batch.append(d)

        d_raw = robust_median_filter(batch)  # 中位數（剔除離群）
        if d_raw <= 0.0:
            print(f"{i+1:04d}  讀取失敗，略過")
            continue

        # 線性校正：先比例再偏移
        d_corr = CAL_A * d_raw + CAL_B
        err_cm = (d_corr - true_d) * 100.0

        errors.append(round(err_cm, 3))
        saved += 1
        print(f"{i+1:04d}  raw={d_raw:.3f} m  corr={d_corr:.3f} m  error_cm={err_cm:.2f}")

    if ser:
        try:
            ser.close()
        except Exception:
            pass

    # ===== 6) 輸出檔案（只有一欄：error_cm）=====
    # CSV（一定會寫）
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['error_cm'])
        for v in errors:
            w.writerow([f"{v:.3f}"])
    print(f"[Info] 已儲存 CSV : {csv_path}（{saved} 筆 error_cm）")

    # Excel（若可用 pandas 或 openpyxl 就寫）
    wrote_excel = False
    if HAS_PANDAS:
        try:
            import pandas as pd  # 再保險一次
            df = pd.DataFrame({'error_cm': errors})
            with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='1D_Range_Error')
            wrote_excel = True
        except Exception as e:
            print(f"[Warn] pandas/openpyxl 寫 Excel 失敗：{e}")

    if (not wrote_excel) and HAS_OPENPYXL:
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = '1D_Range_Error'
            ws.append(['error_cm'])
            for v in errors:
                ws.append([float(f"{v:.3f}")])
            wb.save(xlsx_path)
            wrote_excel = True
        except Exception as e:
            print(f"[Warn] openpyxl 寫 Excel 失敗：{e}")

    if wrote_excel:
        print(f"[Info] 已儲存 Excel: {xlsx_path}（{saved} 筆 error_cm）")
    else:
        print("[Info] 未寫入 Excel（環境無 pandas/openpyxl 或寫入失敗），已完成 CSV。")


if __name__ == "__main__":
    main()
