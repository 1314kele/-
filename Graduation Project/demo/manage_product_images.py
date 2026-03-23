"""
商品图片管理脚本
提供多种方式给商品添加图片
"""

import os
import random
from django.utils import timezone
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')
django.setup()

from marketplace.models import Product


def list_products_without_images():
    """列出所有没有图片的商品"""
    products = Product.objects.filter(image='') | Product.objects.filter(image__isnull=True)
    print(f'找到 {len(products)} 个没有图片的商品:')
    for i, product in enumerate(products, 1):
        print(f'{i}. {product.id} - {product.title} - ¥{product.price}')
    return products


def add_placeholder_image_to_product(product_id, text=None):
    """
    给指定商品添加占位图
    
    Args:
        product_id: 商品ID
        text: 占位图上的文字（默认使用商品标题）
    """
    try:
        product = Product.objects.get(id=product_id)
        
        if not text:
            text = product.title[:20]
        
        # 生成占位图文件名
        filename = f'placeholder_{product.id}_{random.randint(1000, 9999)}.jpg'
        
        # 创建简单的占位图
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (400, 300), color=(102, 126, 234))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # 绘制文字
        text_lines = [text[i:i+15] for i in range(0, len(text), 15)]
        y_offset = 100
        for line in text_lines:
            try:
                text_width, text_height = draw.textsize(line, font=font)
            except:
                text_width, text_height = 200, 30
            position = ((400 - text_width) // 2, y_offset)
            draw.text(position, line, fill=(255, 255, 255), font=font)
            y_offset += text_height + 10
        
        # 添加分类标签
        category_text = f'分类: {product.category.name}'
        try:
            text_width, text_height = draw.textsize(category_text, font=font)
        except:
            text_width, text_height = 200, 30
        position = ((400 - text_width) // 2, 250)
        draw.text(position, category_text, fill=(220, 220, 220), font=font)
        
        # 确保media/products目录存在
        media_dir = os.path.join(os.path.dirname(__file__), 'media', 'products')
        os.makedirs(media_dir, exist_ok=True)
        
        filepath = os.path.join(media_dir, filename)
        img.save(filepath, 'JPEG', quality=85)
        
        # 更新商品图片
        product.image = f'products/{filename}'
        product.save()
        
        print(f'✓ 成功给商品 "{product.title}" 添加占位图')
        return True
        
    except Product.DoesNotExist:
        print(f'✗ 找不到ID为 {product_id} 的商品')
        return False
    except Exception as e:
        print(f'✗ 添加图片失败: {e}')
        import traceback
        traceback.print_exc()
        return False


def add_placeholder_images_to_all_products():
    """给所有没有图片的商品添加占位图"""
    products = Product.objects.filter(image='') | Product.objects.filter(image__isnull=True)
    print(f'准备给 {len(products)} 个商品添加占位图...')
    
    success_count = 0
    for product in products:
        if add_placeholder_image_to_product(product.id):
            success_count += 1
    
    print(f'\n完成！成功给 {success_count}/{len(products)} 个商品添加了图片')


def clear_product_image(product_id):
    """清除指定商品的图片"""
    try:
        product = Product.objects.get(id=product_id)
        if product.image:
            # 删除文件
            image_path = os.path.join(os.path.dirname(__file__), 'media', product.image.name)
            if os.path.exists(image_path):
                os.remove(image_path)
            # 清除数据库记录
            product.image = None
            product.save()
            print(f'✓ 已清除商品 "{product.title}" 的图片')
        else:
            print(f'商品 "{product.title}" 没有图片')
        return True
    except Product.DoesNotExist:
        print(f'✗ 找不到ID为 {product_id} 的商品')
        return False


def main():
    """主函数 - 交互式菜单"""
    print('=' * 50)
    print('商品图片管理工具')
    print('=' * 50)
    
    while True:
        print('\n请选择操作:')
        print('1. 列出没有图片的商品')
        print('2. 给指定商品添加占位图')
        print('3. 给所有没有图片的商品添加占位图')
        print('4. 清除指定商品的图片')
        print('5. 退出')
        
        choice = input('\n请输入选项 (1-5): ').strip()
        
        if choice == '1':
            list_products_without_images()
        
        elif choice == '2':
            product_id = input('请输入商品ID: ').strip()
            if product_id.isdigit():
                add_placeholder_image_to_product(int(product_id))
            else:
                print('请输入有效的数字ID')
        
        elif choice == '3':
            confirm = input('确定要给所有没有图片的商品添加占位图吗？(y/n): ').strip().lower()
            if confirm == 'y':
                add_placeholder_images_to_all_products()
        
        elif choice == '4':
            product_id = input('请输入商品ID: ').strip()
            if product_id.isdigit():
                clear_product_image(int(product_id))
            else:
                print('请输入有效的数字ID')
        
        elif choice == '5':
            print('再见！')
            break
        
        else:
            print('无效的选项，请重新输入')


if __name__ == '__main__':
    main()
