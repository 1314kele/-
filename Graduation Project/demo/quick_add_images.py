"""
快速给商品添加占位图
"""

import os
import random
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')
django.setup()

from marketplace.models import Product


def add_placeholder_image_to_product(product):
    """给单个商品添加占位图"""
    try:
        text = product.title[:20]
        
        # 生成占位图文件名
        filename = f'placeholder_{product.id}_{random.randint(1000, 9999)}.jpg'
        
        # 创建简单的占位图
        from PIL import Image, ImageDraw, ImageFont
        
        # 根据分类选择不同的背景色
        bg_colors = [
            (102, 126, 234),   # 蓝色
            (118, 75, 162),    # 紫色
            (246, 224, 94),    # 黄色
            (230, 126, 34),    # 橙色
            (52, 152, 219),    # 浅蓝色
            (155, 89, 182),    # 深紫色
            (46, 204, 113),    # 绿色
            (231, 76, 60),     # 红色
            (52, 73, 94),      # 深灰色
            (149, 165, 166),   # 浅灰色
        ]
        
        bg_color = random.choice(bg_colors)
        img = Image.new('RGB', (400, 300), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # 绘制文字
        text_lines = [text[i:i+15] for i in range(0, len(text), 15)]
        y_offset = 80
        for line in text_lines:
            try:
                text_width, text_height = draw.textsize(line, font=font)
            except:
                text_width, text_height = 200, 30
            position = ((400 - text_width) // 2, y_offset)
            draw.text(position, line, fill=(255, 255, 255), font=font)
            y_offset += text_height + 10
        
        # 添加价格标签
        price_text = f'¥{product.price}'
        try:
            price_font = ImageFont.truetype("arial.ttf", 32)
        except:
            price_font = ImageFont.load_default()
        
        try:
            text_width, text_height = draw.textsize(price_text, font=price_font)
        except:
            text_width, text_height = 150, 40
        
        # 价格背景框
        box_padding = 10
        box_x1 = (400 - text_width) // 2 - box_padding
        box_y1 = 200 - box_padding
        box_x2 = (400 + text_width) // 2 + box_padding
        box_y2 = 200 + text_height + box_padding
        
        draw.rectangle([box_x1, box_y1, box_x2, box_y2], fill=(0, 0, 0, 128))
        position = ((400 - text_width) // 2, 200)
        draw.text(position, price_text, fill=(255, 215, 0), font=price_font)
        
        # 添加分类标签
        category_text = product.category.name
        try:
            text_width, text_height = draw.textsize(category_text, font=font)
        except:
            text_width, text_height = 200, 30
        position = ((400 - text_width) // 2, 260)
        draw.text(position, category_text, fill=(220, 220, 220), font=font)
        
        # 确保media/products目录存在
        media_dir = os.path.join(os.path.dirname(__file__), 'media', 'products')
        os.makedirs(media_dir, exist_ok=True)
        
        filepath = os.path.join(media_dir, filename)
        img.save(filepath, 'JPEG', quality=85)
        
        # 更新商品图片
        product.image = f'products/{filename}'
        product.save()
        
        print(f'✓ {product.title}')
        return True
        
    except Exception as e:
        print(f'✗ {product.title} - 失败: {e}')
        return False


def main():
    """主函数"""
    print('=' * 50)
    print('快速添加商品占位图')
    print('=' * 50)
    
    # 获取所有没有图片的商品
    products = Product.objects.filter(image='') | Product.objects.filter(image__isnull=True)
    print(f'\n找到 {len(products)} 个没有图片的商品\n')
    
    if len(products) == 0:
        print('所有商品都已有图片！')
        return
    
    print('开始添加占位图...\n')
    
    success_count = 0
    for product in products:
        if add_placeholder_image_to_product(product):
            success_count += 1
    
    print(f'\n{"=" * 50}')
    print(f'完成！成功给 {success_count}/{len(products)} 个商品添加了图片')
    print(f'{"=" * 50}')


if __name__ == '__main__':
    main()
