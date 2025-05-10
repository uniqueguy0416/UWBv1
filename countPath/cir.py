import serial
import matplotlib.pyplot as plt
import os
from datetime import datetime

# ── 設定 ──
serial_port = '/dev/ttyUSB0'
baud_rate = 57600
output_dir = "/home/e520/UWBv1/countPath/output"
os.makedirs(output_dir, exist_ok=True)

# ── 初始化 Serial ──
ser = serial.Serial(serial_port, baud_rate, timeout=1)
print(f"📡 開始從 {serial_port} 讀取 CIR 資料...")

anchor_id = "0241000000000000"
cir_data = []

# ── 讀取資料 ──
while True:
    try:
        raw = ser.readline()
        line = raw.decode(errors='ignore').strip()
    except Exception as e:
        print(f"⚠️ 解碼錯誤：{e}")
        continue

    if line.startswith("ANCHOR_ID"):
        anchor_id = line.split(":")[1]
        cir_data = []
        print(f"🛰️  偵測到 Anchor ID: {anchor_id}")
    elif line.isdigit():
        cir_data.append(int(line))
        if len(cir_data) == 1024:
            print("📈 成功讀取 1024 筆 CIR 資料")
            break

# ── 畫圖 ──
plt.figure(figsize=(10, 4))
plt.plot(cir_data)
plt.title(f"DW1000 CIR 波形 - Anchor {anchor_id}")
plt.xlabel("樣本點")
plt.ylabel("振幅")
plt.grid(True)

# ── 儲存圖表 ──
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = os.path.join(output_dir, f"cir_anchor{anchor_id}_{timestamp}.png")
plt.savefig(output_path)
print(f"✅ CIR 波形已儲存：{output_path}")

# ── 顯示圖表 ──
plt.show()
