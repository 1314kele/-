#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from marketplace.models import Category

print("=== 创建示例分类数据 ===")

# 定义示例分类
sample_categories = [
    {
        'name': '电子产品',
        'description': '手机、电脑、平板、耳机等电子设备'
    },
    {
        'name': '学习用品',
        'description': '教材、参考书、文具、学习工具'
    },
    {
        'name': '生活用品',
        'description': '日用品、洗漱用品、收纳用品等'
    },
    {
        'name': '服装鞋帽',
        'description': '衣服、鞋子、帽子、配饰等'
    },
    {
        'name': '运动器材',
        'description': '球类、健身器材、运动装备等'
    },
    {
        'name': '书籍资料',
        'description': '小说、专业书籍、学习资料等'
    },
    {
        'name': '其他物品',
        'description': '其他未分类的闲置物品'
    }
]

created_count = 0
for category_data in sample_categories:
    # 检查是否已存在同名分类
    if not Category.objects.filter(name=category_data['name']).exists():
        category = Category.objects.create(**category_data)
        print(f"创建分类: {category.name}")
        created_count += 1
    else:
        print(f"分类已存在: {category_data['name']}")

print(f"\n=== 完成创建 {created_count} 个分类 ===")

# 显示所有分类
print("\n当前所有分类:")
for cat in Category.objects.all():
    print(f"ID: {cat.id}, 名称: {cat.name}, 描述: {cat.description}")