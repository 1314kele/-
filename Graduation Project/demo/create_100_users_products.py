#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django
import random
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth.models import User
from marketplace.models import Category, Product, Favorite, Review

print('=== 开始创建100个用户和商品数据 ===')

# 检查分类是否存在
categories = Category.objects.all()
if categories.count() == 0:
    print('错误：没有找到任何分类，请先运行 create_sample_categories.py')
    sys.exit(1)

print(f'找到 {categories.count()} 个分类')

# 创建100个用户
users = []
for i in range(1, 101):
    username = f'testuser{i:03d}'
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            password='password123',
            email=f'{username}@example.com'
        )
        users.append(user)
        print(f'创建用户: {username}')
    else:
        user = User.objects.get(username=username)
        users.append(user)
        print(f'用户已存在: {username}')

print(f'成功处理 {len(users)} 个用户')

# 为每个用户创建3-5个商品
products = []
product_conditions = ['new', 'like_new', 'good', 'fair', 'poor']
product_statuses = ['available', 'available', 'available', 'sold', 'reserved']  # 大部分为可交易

for user in users:
    num_products = random.randint(3, 5)
    for i in range(num_products):
        category = random.choice(categories)
        condition = random.choice(product_conditions)
        status = random.choice(product_statuses)
        
        product = Product.objects.create(
            title=f'{user.username}的商品{i+1}',
            description=f'这是{user.username}发布的第{i+1}个商品，商品状况良好，欢迎购买。',
            price=round(random.uniform(10.0, 500.0), 2),
            category=category,
            seller=user,
            condition=condition,
            status=status,
            location='校园内',
            contact_info=f'电话：13800138000，微信：{user.username}',
            views=random.randint(0, 100)
        )
        products.append(product)
        print(f'创建商品: {product.title} (价格: {product.price:.2f})')

print(f'成功创建 {len(products)} 个商品')

# 创建收藏记录（约200条）
favorites_created = 0
for _ in range(200):
    user = random.choice(users)
    product = random.choice(products)
    
    # 确保用户不能收藏自己的商品
    if user != product.seller:
        if not Favorite.objects.filter(user=user, product=product).exists():
            Favorite.objects.create(user=user, product=product)
            favorites_created += 1

print(f'创建 {favorites_created} 条收藏记录')

# 创建评价记录（约150条）
reviews_created = 0
for _ in range(150):
    reviewer = random.choice(users)
    product = random.choice(products)
    
    # 确保评价者不是卖家，且没有重复评价
    if reviewer != product.seller:
        if not Review.objects.filter(reviewer=reviewer, product=product).exists():
            rating = random.randint(3, 5)  # 大部分为好评
            Review.objects.create(
                reviewer=reviewer,
                reviewed_user=product.seller,
                product=product,
                rating=rating,
                comment=f'商品描述准确，卖家服务很好，交易过程顺利。'
            )
            reviews_created += 1

print(f'创建 {reviews_created} 条评价记录')

print('\\n=== 数据创建完成 ===')
print(f'总用户数: {User.objects.count()}')
print(f'总商品数: {Product.objects.count()}')
print(f'总收藏数: {Favorite.objects.count()}')
print(f'总评价数: {Review.objects.count()}')
print('=== 脚本执行完毕 ===')
