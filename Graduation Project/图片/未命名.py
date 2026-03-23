from PIL import Image, ImageDraw, ImageFont

# ---------------------- 配置 ----------------------
WIDTH = 800
HEIGHT = 900
BG_COLOR = (255, 255, 255)
TEXT_COLOR = (0, 0, 0)
BOX_COLOR = (0, 0, 0)

# 尝试加载合适字体，没有则用默认
try:
    font_title = ImageFont.truetype("simhei.ttf", 24)
    font_text = ImageFont.truetype("simhei.ttf", 18)
except:
    font_title = ImageFont.load_default(size=24)
    font_text = ImageFont.load_default(size=18)

# ---------------------- 创建画布 ----------------------
img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(img)

# ---------------------- 绘制模块 ----------------------
def draw_module(x, y, w, h, lines):
    draw.rectangle([x, y, x+w, y+h], outline=BOX_COLOR, width=2)
    ty = y + 15
    for line in lines:
        tx = x + (w - draw.textlength(line, font=font_text)) // 2
        draw.text((tx, ty), line, fill=TEXT_COLOR, font=font_text)
        ty += 25
    return y + h

# 计算居中位置
center_x = WIDTH // 2
module_width = 320

# 绘制各个层
y1 = draw_module(center_x - module_width//2, 50, module_width, 60, ["用户层"])
y2 = draw_module(center_x - module_width//2, y1+40, module_width, 100, ["表现层(前端)", "HTML/CSS/JS", "Bootstrap"])
y3 = draw_module(center_x - module_width//2, y2+40, module_width, 280, [
    "业务逻辑层(后端)",
    "Django框架",
    "用户管理模块",
    "商品管理模块",
    "搜索模块",
    "推荐模块",
    "混合推荐算法",
    "交易模块",
    "评价模块",
    "消息模块"
])
y4 = draw_module(center_x - module_width//2, y3+40, module_width, 90, ["数据层", "MySQL数据库", "Redis缓存"])

# ---------------------- 绘制箭头 ----------------------
def draw_arrow(x, y1, y2):
    # 计算模块间距的中间位置
    gap_start = y1
    gap_end = y2
    gap_mid = (gap_start + gap_end) / 2
    
    # 箭头只画在中间一小段，不接触模块
    arrow_start = gap_mid - 10
    arrow_end = gap_mid + 10
    
    # 绘制箭头线条
    draw.line([x, arrow_start, x, arrow_end], fill=BOX_COLOR, width=2)
    
    # 绘制更美观的箭头三角形
    draw.polygon([
        (x - 6, arrow_end - 8), 
        (x + 6, arrow_end - 8), 
        (x, arrow_end)
    ], fill=BOX_COLOR)

draw_arrow(center_x, y1, y2)
draw_arrow(center_x, y2, y3)
draw_arrow(center_x, y3, y4)

# ---------------------- 保存图片 ----------------------
img.save("校园二手交易系统架构图.png")
print("✅ 高清架构图已生成：校园二手交易系统架构图.png")
img.show()
