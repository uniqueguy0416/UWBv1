import pandas as pd
import matplotlib.pyplot as plt

csv_path = r'C:\RpiUploads\uwb_datav2.csv'
df = pd.read_csv(csv_path)

# 取出 Tag 座標
tag_x = df['tag_x']
tag_y = df['tag_y']
tag_z = df['tag_z']

# 定義 Anchor 座標
anchor_positions = [
    (0.00,  0.00, 1.00),  # anchor6
    (5.00,  0.00, 1.00),  # anchor7
    (5.00, 10.00, 1.00),  # anchor8
    (0.00, 10.00, 1.00)   # anchor9
]
anchor_x, anchor_y, anchor_z = zip(*anchor_positions)

# 繪製 3D 圖
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Tag 點雲
ax.scatter(tag_x, tag_y, tag_z)

# Anchor 位置
ax.scatter(anchor_x, anchor_y, anchor_z, marker='^')

# 標籤與設定
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
ax.set_zlabel('Z (m)')
ax.set_title('UWB 3D 定位結果')
ax.set_box_aspect((1,1,1))  # 等比例顯示

plt.show()