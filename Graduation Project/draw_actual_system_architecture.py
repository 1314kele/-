import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as lines

# 创建图表
fig, ax = plt.subplots(figsize=(18, 14))

# 清空坐标轴
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# 绘制标题
plt.title('校园二手交易系统架构图', fontsize=20, fontweight='bold')

# 定义层级位置
y_levels = [90, 70, 45, 20, 5]
layer_heights = [15, 20, 20, 10, 10]
layer_width = 90
layer_x = 5

# 绘制用户层
user_layer = patches.Rectangle((layer_x, y_levels[0]), layer_width, layer_heights[0], 
                             edgecolor='#01579b', facecolor='#e1f5ff', linewidth=2)
ax.add_patch(user_layer)
plt.text(50, y_levels[0] + layer_heights[0]/2, '用户层', ha='center', va='center', fontsize=16, fontweight='bold')
plt.text(50, y_levels[0] + layer_heights[0]/2 - 3, '浏览器/移动设备', ha='center', va='center', fontsize=12)

# 绘制表现层
presentation_layer = patches.Rectangle((layer_x, y_levels[1]), layer_width, layer_heights[1], 
                                    edgecolor='#2e7d32', facecolor='#90ee90', linewidth=2)
ax.add_patch(presentation_layer)
plt.text(50, y_levels[1] + layer_heights[1]/2, '表现层 (前端)', ha='center', va='center', fontsize=16, fontweight='bold')
plt.text(50, y_levels[1] + layer_heights[1]/2 - 3, 'HTML/CSS/JS, Bootstrap 5', ha='center', va='center', fontsize=12)

# 绘制前端页面模块
frontend_modules = ['首页', '商品列表', '商品详情', '发布商品', '用户中心', '消息中心', '订单管理', '钱包管理']
module_y = y_levels[1] + 7
for i, module in enumerate(frontend_modules):
    x = 12 + (i % 4) * 20
    if i >= 4:
        x = 12 + (i-4) * 20
        module_y = y_levels[1] + 2
    plt.text(x, module_y, module, ha='center', va='center', fontsize=10)

# 绘制业务逻辑层
business_layer = patches.Rectangle((layer_x, y_levels[2]), layer_width, layer_heights[2], 
                                edgecolor='#f57c00', facecolor='#fff9c4', linewidth=2)
ax.add_patch(business_layer)
plt.text(50, y_levels[2] + layer_heights[2]/2, '业务逻辑层 (后端)', ha='center', va='center', fontsize=16, fontweight='bold')
plt.text(50, y_levels[2] + layer_heights[2]/2 - 3, 'Django 3.2+, Python 3.7+', ha='center', va='center', fontsize=12)

# 绘制核心模块
business_modules = ['用户管理', '商品管理', '交易管理', '消息通知', '评价系统', '推荐系统', '搜索功能', '安全系统', '行为分析', '地图功能']
module_y = y_levels[2] + 8
for i, module in enumerate(business_modules):
    x = 10 + (i % 5) * 17
    if i >= 5:
        x = 10 + (i-5) * 17
        module_y = y_levels[2] + 2
    plt.text(x, module_y, module, ha='center', va='center', fontsize=9)

# 绘制API层
api_layer = patches.Rectangle((layer_x, y_levels[3]), layer_width, layer_heights[3], 
                            edgecolor='#7b1fa2', facecolor='#f3e5f5', linewidth=2)
ax.add_patch(api_layer)
plt.text(50, y_levels[3] + layer_heights[3]/2, 'API层', ha='center', va='center', fontsize=14, fontweight='bold')
plt.text(50, y_levels[3] + layer_heights[3]/2 - 2, 'RESTful API, AJAX接口', ha='center', va='center', fontsize=10)

# 绘制数据层
data_layer = patches.Rectangle((layer_x, y_levels[4]), layer_width, layer_heights[4], 
                            edgecolor='#666666', facecolor='#d3d3d3', linewidth=2)
ax.add_patch(data_layer)
plt.text(50, y_levels[4] + layer_heights[4]/2, '数据层', ha='center', va='center', fontsize=14, fontweight='bold')
plt.text(50, y_levels[4] + layer_heights[4]/2 - 2, 'SQLite, 文件存储 (商品图片)', ha='center', va='center', fontsize=10)

# 绘制连接线
for i in range(4):
    line = lines.Line2D([50, 50], 
                       [y_levels[i] - layer_heights[i]/2, y_levels[i+1] + layer_heights[i+1]/2], 
                       color='black', linestyle='-', linewidth=1)
    ax.add_line(line)
    # 绘制箭头
    plt.arrow(50, y_levels[i+1] + layer_heights[i+1]/2, 0, -2, head_width=2, head_length=2, fc='black', ec='black')

# 调整布局
plt.tight_layout()

# 保存图表
plt.savefig('actual_system_architecture.png', dpi=150, bbox_inches='tight')

# 显示图表
plt.show()

print("系统架构图已绘制完成并保存为 actual_system_architecture.png")