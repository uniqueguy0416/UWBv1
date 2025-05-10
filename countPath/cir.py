import serial
import matplotlib.pyplot as plt

# 設定 serial port（根據你接到哪個 ttyUSB）
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

# 等待 "ANCHOR_ID" 開頭的訊息
anchor_id = ['0241000000000000']
cir_data = []

while True:
    line = ser.readline().decode().strip()
    if line.startswith("ANCHOR_ID"):
        anchor_id = line.split(":")[1]
        cir_data = []
    elif line.isdigit():
        cir_data.append(int(line))
        if len(cir_data) == 1024:
            break

# 畫圖
plt.plot(cir_data)
plt.title(f"CIR 波形 - Anchor {anchor_id}")
plt.xlabel("樣本點")
plt.ylabel("振幅")
plt.grid(True)
plt.show()
