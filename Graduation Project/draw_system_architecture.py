import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as lines

# 创建图表
fig, ax = plt.subplots(figsize=(16, 12))

# 清空坐标轴
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# 绘制标题
plt.title('校园二手交易系统架构图', fontsize=18, fontweight='bold')

# 定义层级位置
y_levels = [85, 60, 35, 10]
layer_heights = [20, 20, 20, 15]
layer_width = 90
layer_x = 5

# 绘制用户层
user_layer = patches.Rectangle((layer_x, y_levels[0]), layer_width, layer_heights[0], 
                             edgecolor='#01579b', facecolor='#e1f5ff', linewidth=2)
ax.add_patch(user_layer)
plt.text(50, y_levels[0] + layer_heights[0]/2, '用户层', ha='center', va='center', fontsize=14, fontweight='bold')
plt.text(50, y_levels[0] + layer_heights[0]/2 - 2, '浏览器/移动设备', ha='center', va='center', fontsize=12)

# 绘制表现层
presentation_layer = patches.Rectangle((layer_x, y_levels[1]), layer_width, layer_heights[1], 
                                    edgecolor='#2e7d32', facecolor='#90ee90', linewidth=2)
ax.add_patch(presentation_layer)
plt.text(50, y_levels[1] + layer_heights[1]/2, '表现层 (前端)', ha='center', va='center', fontsize=14, fontweight='bold')
plt.text(50, y_levels[1] + layer_heights[1]/2 - 2, 'HTML/CSS/JS, Bootstrap', ha='center', va='center', fontsize=12)

# 绘制业务逻辑层
business_layer = patches.Rectangle((layer_x, y_levels[2]), layer_width, layer_heights[2], 
                                edgecolor='#f57c00', facecolor='#fff9c4', linewidth=2)
ax.add_patch(business_layer)
plt.text(50, y_levels[2] + layer_heights[2]/2, '业务逻辑层 (后端)', ha='center', va='center', fontsize=14, fontweight='bold')
plt.text(50, y_levels[2] + layer_heights[2]/2 - 2, 'Django 3.2+, Python 3.7+', ha='center', va='center', fontsize=12)

# 绘制核心模块
modules = ['用户管理', '商品管理', '搜索模块', '推荐模块', '交易模块', '评价模块', '消息模块', '安全模块']
module_y = y_levels[2] + 5
for i, module in enumerate(modules):
    x = 15 + (i % 4) * 20
    if i >= 4:
        x = 15 + (i-4) * 20
        module_y = y_levels[2] + 1
    plt.text(x, module_y, module, ha='center', va='center', fontsize=10)

# 绘制数据层
data_layer = patches.Rectangle((layer_x, y_levels[3]), layer_width, layer_heights[3], 
                            edgecolor='#666666', facecolor='#d3d3d3', linewidth=2)
ax.add_patch(data_layer)
plt.text(50, y_levels[3] + layer_heights[3]/2, '数据层', ha='center', va='center', fontsize=14, fontweight='bold')
plt.text(50, y_levels[3] + layer_heights[3]/2 - 2, 'MySQL 8.0+, Redis', ha='center', va='center', fontsize=12)

# 绘制连接线
for i in range(3):
    line = lines.Line2D([50, 50], 
                       [y_levels[i] - layer_heights[i]/2, y_levels[i+1] + layer_heights[i+1]/2], 
                       color='black', linestyle='-', linewidth=1)
    ax.add_line(line)
    # 绘制箭头
    plt.arrow(50, y_levels[i+1] + layer_heights[i+1]/2, 0, -2, head_width=2, head_length=2, fc='black', ec='black')

# 调整布局
plt.tight_layout()

# 保存图表
plt.savefig('system_architecture.png', dpi=150, bbox_inches='tight')

# 显示图表
plt.show()

print("系统架构图已绘制完成并保存为 system_architecture.png")