import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime

# ── 設定儲存路徑 ──
OUTPUT_DIR = "/home/e520/UWBv1/countPath/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 模擬參數 ──
anchor_id = "0241000000000000"
sample_points = 1024

# ── 產生模擬 CIR 波形資料 ──
print("🧪 測試模式啟動：產生模擬 CIR 資料...")
cir_data = [int(200 + 50 * np.sin(i * 0.02)) for i in range(sample_points)]

# ── 畫圖 ──
plt.figure(figsize=(10, 4))
plt.plot(cir_data)
plt.title(f"模擬 CIR 波形 - Anchor {anchor_id}")
plt.xlabel("樣本點")
plt.ylabel("振幅")
plt.grid(True)

# ── 儲存圖片 ──
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = os.path.join(OUTPUT_DIR, f"cir_anchor{anchor_id}_{timestamp}_test.png")
plt.savefig(output_path)
print(f"✅ 測試 CIR 圖片已儲存：{output_path}")

# ── 顯示圖 ──
plt.show()
