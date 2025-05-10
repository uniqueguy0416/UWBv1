import serial
import matplotlib.pyplot as plt
import os
from datetime import datetime

# ── 串口設定 ──
COM_PORT = '/dev/ttyUSB0'
BAUD_RATE = 57600
OUTPUT_DIR = "/home/e520/UWBv1"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 初始化串口 ──
try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"✅ 已連線至 {COM_PORT}（波特率：{BAUD_RATE}）")
except Exception as e:
    print(f"❌ 無法連線至 {COM_PORT}：{e}")
    exit(1)

# ── 資料準備 ──
anchor_id = "0241000000000000"
cir_data = []
print("📡 等待 anchor 傳送 CIR 資料...")

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
        if len(cir_data) % 100 == 0:
            print(f"📥 已接收 {len(cir_data)} / 1024 筆資料...")
        if len(cir_data) == 1024:
            print("✅ 成功接收 1024 筆 CIR 資料！")
            break

# ── 畫圖與儲存 ──
plt.figure(figsize=(10, 4))
plt.plot(cir_data)
plt.title(f"CIR 波形 - Anchor {anchor_id}")
plt.xlabel("樣本點")
plt.ylabel("振幅")
plt.grid(True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = os.path.join(OUTPUT_DIR, f"cir_anchor{anchor_id}_{timestamp}.png")
plt.savefig(output_path)
print(f"✅ 圖片已儲存：{output_path}")

plt.show()
