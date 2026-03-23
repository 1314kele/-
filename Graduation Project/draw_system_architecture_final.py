import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as lines
import matplotlib.font_manager as fm
import os

# 查找可用的中文字体
def find_chinese_font():
    # 尝试常见的中文字体
    chinese_fonts = ['SimHei', 'Microsoft YaHei', 'STSong', 'SimSun', 'KaiTi', 'FangSong']
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    for font in chinese_fonts:
        if font in available_fonts:
            return font
    
    # 如果没有找到，尝试查找包含中文字符的字体
    for font in available_fonts:
        if any(keyword in font for keyword in ['Sim', 'Hei', 'Song', 'Kai', 'Ming', 'Chinese']):
            return font
    
    return None

# 设置中文字体
chinese_font = find_chinese_font()
if chinese_font:
    plt.rcParams['font.sans-serif'] = [chinese_font]
    print(f"使用字体: {chinese_font}")
else:
    print("警告: 未找到中文字体，使用默认字体")

plt.rcParams['axes.unicode_minus'] = False

# 创建图表
fig, ax = plt.subplots(figsize=(16, 12))

# 清空坐标轴
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# 绘制标题
ax.text(50, 97, '校园二手交易系统架构图', ha='center', va='center', fontsize=20, fontweight='bold')

# 定义层级位置
y_levels = [85, 65, 40, 15]
layer_heights = [18, 22, 28, 18]
layer_width = 88
layer_x = 6

# 绘制用户层
user_layer = patches.Rectangle((layer_x, y_levels[0]), layer_width, layer_heights[0], 
                             edgecolor='#01579b', facecolor='#e1f5ff', linewidth=2)
ax.add_patch(user_layer)
ax.text(50, y_levels[0] + layer_heights[0]/2 + 2, '用户层', ha='center', va='center', fontsize=16, fontweight='bold')
ax.text(50, y_levels[0] + layer_heights[0]/2 - 3, '浏览器 / 移动设备', ha='center', va='center', fontsize=12)

# 绘制表现层
presentation_layer = patches.Rectangle((layer_x, y_levels[1]), layer_width, layer_heights[1], 
                                    edgecolor='#2e7d32', facecolor='#c8e6c9', linewidth=2)
ax.add_patch(presentation_layer)
ax.text(50, y_levels[1] + layer_heights[1]/2 + 5, '表现层 (前端)', ha='center', va='center', fontsize=16, fontweight='bold')
ax.text(50, y_levels[1] + layer_heights[1]/2 + 1, 'HTML / CSS / JavaScript, Bootstrap 5', ha='center', va='center', fontsize=11)

# 绘制前端页面模块
frontend_modules = ['首页', '商品列表', '商品详情', '发布商品', '用户中心', '消息中心', '订单管理', '钱包管理']
module_y = y_levels[1] + 5
for i, module in enumerate(frontend_modules):
    x = 12 + (i % 4) * 20
    if i >= 4:
        x = 12 + (i-4) * 20
        module_y = y_levels[1] + 1
    ax.text(x, module_y, module, ha='center', va='center', fontsize=10, 
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.8))

# 绘制业务逻辑层
business_layer = patches.Rectangle((layer_x, y_levels[2]), layer_width, layer_heights[2], 
                                edgecolor='#f57c00', facecolor='#ffe0b2', linewidth=2)
ax.add_patch(business_layer)
ax.text(50, y_levels[2] + layer_heights[2]/2 + 8, '业务逻辑层 (后端)', ha='center', va='center', fontsize=16, fontweight='bold')
ax.text(50, y_levels[2] + layer_heights[2]/2 + 4, 'Django 3.2+, Python 3.7+', ha='center', va='center', fontsize=11)

# 绘制核心模块
business_modules = ['用户管理', '商品管理', '交易管理', '消息通知', '评价系统', 
                   '推荐系统', '搜索功能', '安全系统', '行为分析', '地图功能']
module_y = y_levels[2] + 9
for i, module in enumerate(business_modules):
    x = 10 + (i % 5) * 17
    if i >= 5:
        x = 10 + (i-5) * 17
        module_y = y_levels[2] + 3
    ax.text(x, module_y, module, ha='center', va='center', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='orange', alpha=0.8))

# 绘制数据层
data_layer = patches.Rectangle((layer_x, y_levels[3]), layer_width, layer_heights[3], 
                            edgecolor='#666666', facecolor='#e0e0e0', linewidth=2)
ax.add_patch(data_layer)
ax.text(50, y_levels[3] + layer_heights[3]/2 + 2, '数据层', ha='center', va='center', fontsize=16, fontweight='bold')
ax.text(50, y_levels[3] + layer_heights[3]/2 - 2, 'SQLite 数据库, 文件存储 (商品图片)', ha='center', va='center', fontsize=11)

# 绘制连接线
for i in range(3):
    line = lines.Line2D([50, 50], 
                       [y_levels[i] - layer_heights[i]/2, y_levels[i+1] + layer_heights[i+1]/2], 
                       color='black', linestyle='-', linewidth=1.5)
    ax.add_line(line)
    # 绘制箭头
    ax.annotate('', xy=(50, y_levels[i+1] + layer_heights[i+1]/2 + 1), 
                xytext=(50, y_levels[i] - layer_heights[i]/2 - 1),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))

# 调整布局
plt.tight_layout()

# 保存图表
output_path = 'system_architecture_final.png'
plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white', edgecolor='none')

print(f"系统架构图已成功生成: {output_path}")
print(f"图片保存在: {os.path.abspath(output_path)}")

# 关闭图表窗口
plt.close()