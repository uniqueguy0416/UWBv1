import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 1. 讀取資料
csv_path = r'C:\RpiUploads\uwb_1m.csv'
df = pd.read_csv(csv_path)

# 2. 定義 Anchor 座標
anchor_positions = [
    (0.00,  0.00, 1.00),  # anchor6
    (5.00,  0.00, 1.00),  # anchor7
    (5.00,  8.00, 1.00),  # anchor8
    (0.00,  8.00, 1.00)   # anchor9
]
anchor_x, anchor_y, anchor_z = zip(*anchor_positions)

# 3. 分組計算每個高度的平均 Tag (x,y)
grouped = (
    df
    .groupby('tag_z')[['tag_x','tag_y']]   # 只聚合 tag_x, tag_y
    .mean()
    .reset_index()                         # 這時只有一個 tag_z 列
)

# 4. 繪製 3D 圖
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Anchor 點
ax.scatter(anchor_x, anchor_y, anchor_z, marker='^', s=80, label='Anchor')

# 每個高度的平均 Tag 位置，並連線到各 Anchor
for _, row in grouped.iterrows():
    tx, ty, tz = row['tag_x'], row['tag_y'], row['tag_z']
    ax.scatter([tx], [ty], [tz], s=50, label=f'Tag z={tz:.2f}')
    for ax_x, ax_y, ax_z in anchor_positions:
        ax.plot([ax_x, tx], [ax_y, ty], [ax_z, tz], 'gray', linewidth=0.5)

# 標籤與配置
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
ax.set_zlabel('Z (m)')
ax.set_title('UWB 3D 定位結果與 Anchor–Tag 連線')
ax.set_box_aspect((1,1,1))
ax.legend()

plt.show()
