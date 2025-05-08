import os
import numpy as np
import pandas as pd
from time import sleep
from smb.SMBConnection import SMBConnection
from read_GIPS_distance import UWBpos  # 根據你的檔名修改

# ── 測量參數設定 ──
actual_distance_cm = 600  # 真實距離（公分）
measure_times      = 20   # 測量次數

# ── 初始化 UWB 裝置與結果容器 ──
uwb = UWBpos()
dist_results = []

print(f"📏 測試 anchor6 與目標間距離，預設真實距離為 {actual_distance_cm} cm")
print("🔍 開始測距...\n")

# ── 執行測距迴圈 ──
for i in range(measure_times):
    dis_to_anchor = uwb.UWB_read()    # 假設回傳 [d1, d2, …]
    raw_value     = dis_to_anchor[0]  # 只取第 0 個 anchor
    dist_cm       = raw_value * 100   # 從公尺轉公分

    # 過濾異常值
    if dist_cm < 1:
        print(f"⚠️ 第 {i+1} 次無效資料（{dist_cm:.2f} cm），跳過\n")
        sleep(0.2)
        continue

    print(f"✅ 第 {i+1} 次距離：{dist_cm:.2f} cm\n")
    dist_results.append(dist_cm)
    sleep(0.2)

# ── 統計分析 ──
mean  = np.mean(dist_results) if dist_results else 0
error = mean - actual_distance_cm
std   = np.std(dist_results) if dist_results else 0

print(" 測試結果統計：")
print(f"🖩 有效測距次數：{len(dist_results)}")
print(f" 平均距離：{mean:.2f} cm")
print(f" 誤差：{error:.2f} cm")
print(f" 標準差：{std:.2f} cm\n")

# ── 匯出成本地 Excel ──
local_filename = "test1.xlsx"
df = pd.DataFrame({
    "測距次序": list(range(1, len(dist_results) + 1)),
    "距離 (cm)": dist_results
})
df.to_excel(local_filename, index=False, engine="openpyxl")
print(f"✅ 本地 Excel 已建立：{local_filename}")

# ── 用 SMB 上傳到 Windows 共用 ──
# 參數設定，請依實際環境修改
WINDOWS_USER     = "Nathan Liao"    # Windows 登入帳號
WINDOWS_PASSWORD = "082311"   # Windows 登入密碼
WINDOWS_CLIENT   = "raspberrypi"    # 任意 client 名稱
WINDOWS_SERVER   = "LAPTOP-R3U4PH5U"    # Windows 主機 NetBIOS 名稱
WINDOWS_IP       = "192.168.0.247"  # Windows 主機 IP
SHARE_NAME       = "distance_data"       # Windows 設定的共用名稱
REMOTE_FILENAME  = local_filename

# 建立 SMB 連線
conn = SMBConnection(
    WINDOWS_USER, WINDOWS_PASSWORD,
    WINDOWS_CLIENT, WINDOWS_SERVER,
    use_ntlm_v2=True
)
if not conn.connect(WINDOWS_IP, 445):
    raise RuntimeError("❌ 無法連線到 Windows，共用上傳失敗，請檢查 IP/帳密/防火牆設定")

# 上傳檔案
with open(local_filename, "rb") as file_obj:
    conn.storeFile(SHARE_NAME, REMOTE_FILENAME, file_obj)

conn.close()
print(f"✅ 已上傳到 Windows 共享：\\\\{WINDOWS_IP}\\{SHARE_NAME}\\{REMOTE_FILENAME}")
