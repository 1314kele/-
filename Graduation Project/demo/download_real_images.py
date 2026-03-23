"""
下载真实商品图片
根据商品分类下载对应的Unsplash真实图片
"""

import os
import random
import requests
from io import BytesIO
from PIL import Image
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')
django.setup()

from marketplace.models import Product, Category


# 按分类对应的Unsplash图片URL
CATEGORY_IMAGES = {
    '电子设备': [
        'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=300&fit=crop',  # 手机
        'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop',  # 笔记本
        'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=300&fit=crop',  # 平板
        'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=300&fit=crop',  # 耳机
        'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=300&fit=crop',  # 手表
        'https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?w=400&h=300&fit=crop',  # 键盘
        'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&h=300&fit=crop',  # 相机
    ],
    '书籍资料': [
        'https://images.unsplash.com/photo-1587829741301-dc798b91add1?w=400&h=300&fit=crop',  # 书籍
        'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=300&fit=crop',  # 书架
        'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=300&fit=crop',  # 书本
        'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=400&h=300&fit=crop',  # 书堆
        'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&h=300&fit=crop',  # 阅读
    ],
    '生活用品': [
        'https://images.unsplash.com/photo-1503602642458-232111445657?w=400&h=300&fit=crop',  # 台灯
        'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=300&fit=crop',  # 水壶
        'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop',  # 椅子
        'https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=400&h=300&fit=crop',  # 家电
        'https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?w=400&h=300&fit=crop',  # 家具
    ],
    '运动器材': [
        'https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=400&h=300&fit=crop',  # 健身器材
        'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400&h=300&fit=crop',  # 运动装备
        'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=300&fit=crop',  # 哑铃
        'https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=400&h=300&fit=crop',  # 健身
        'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=300&fit=crop',  # 运动鞋
    ],
    '学习用品': [
        'https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=400&h=300&fit=crop',  # 学习用品
        'https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=400&h=300&fit=crop',  # 笔记本
        'https://images.unsplash.com/photo-1587614382346-4ec70e388b28?w=400&h=300&fit=crop',  # 文具
        'https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400&h=300&fit=crop',  # 电脑
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=300&fit=crop',  # 办公
    ],
    '电子产品': [
        'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=300&fit=crop',  # 手机
        'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop',  # 笔记本
        'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=300&fit=crop',  # 平板
        'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=300&fit=crop',  # 耳机
        'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=300&fit=crop',  # 手表
    ],
    '图书教材': [
        'https://images.unsplash.com/photo-1587829741301-dc798b91add1?w=400&h=300&fit=crop',  # 书籍
        'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=300&fit=crop',  # 书架
        'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=300&fit=crop',  # 书本
    ],
    '服装鞋帽': [
        'https://images.unsplash.com/photo-1556906781-9a412961c28c?w=400&h=300&fit=crop',  # 衣服
        'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=300&fit=crop',  # 鞋子
        'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=400&h=300&fit=crop',  # 购物
        'https://images.unsplash.com/photo-1593030660038-5a6e1984bcd8?w=400&h=300&fit=crop',  # 服饰
    ],
    '运动户外': [
        'https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=400&h=300&fit=crop',  # 健身
        'https://images.unsplash.com/photo-1461896836934-ffe607ba821?w=400&h=300&fit=crop',  # 跑步
        'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&h=300&fit=crop',  # 户外
    ],
    '美妆护肤': [
        'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&h=300&fit=crop',  # 美妆
        'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&h=300&fit=crop',  # 护肤
        'https://images.unsplash.com/photo-1560750937-3d8b3d9bda38?w=400&h=300&fit=crop',  # 化妆品
    ],
}


# 通用备用图片
GENERIC_IMAGES = [
    'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=300&fit=crop',
]


def download_and_save_image(url, filename):
    """下载图片并保存"""
    try:
        print(f'  正在下载: {url[:60]}...')
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img = img.convert('RGB')
            img = img.resize((400, 300), Image.LANCZOS)
            
            # 确保media/products目录存在
            media_dir = os.path.join(os.path.dirname(__file__), 'media', 'products')
            os.makedirs(media_dir, exist_ok=True)
            
            filepath = os.path.join(media_dir, filename)
            img.save(filepath, 'JPEG', quality=85)
            print(f'  ✓ 下载成功: {filename}')
            return f'products/{filename}'
        else:
            print(f'  ✗ 下载失败: HTTP {response.status_code}')
            return None
    except Exception as e:
        print(f'  ✗ 下载异常: {e}')
        return None


def add_real_image_to_product(product):
    """给商品添加真实图片"""
    category_name = product.category.name
    
    # 获取该分类的图片列表
    if category_name in CATEGORY_IMAGES:
        image_urls = CATEGORY_IMAGES[category_name]
    else:
        image_urls = GENERIC_IMAGES
    
    # 随机选择一个图片
    image_url = random.choice(image_urls)
    
    # 生成文件名
    safe_title = ''.join(c if c.isalnum() else '_' for c in product.title[:15])
    filename = f'{safe_title}_{product.id}_{random.randint(1000, 9999)}.jpg'
    
    # 下载并保存图片
    image_path = download_and_save_image(image_url, filename)
    
    if image_path:
        product.image = image_path
        product.save()
        return True
    return False


def main():
    """主函数"""
    print('=' * 60)
    print('下载真实商品图片 - 按分类匹配')
    print('=' * 60)
    
    # 获取所有商品
    products = Product.objects.all()
    print(f'\n找到 {len(products)} 个商品\n')
    
    success_count = 0
    fail_count = 0
    
    for i, product in enumerate(products, 1):
        print(f'[{i}/{len(products)}] {product.title} ({product.category.name})')
        
        if add_real_image_to_product(product):
            success_count += 1
        else:
            fail_count += 1
        
        print()
    
    print('=' * 60)
    print(f'完成！成功: {success_count}, 失败: {fail_count}')
    print('=' * 60)


if __name__ == '__main__':
    main()
