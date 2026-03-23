#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from marketplace.models import Category

print("=== 检查分类数据 ===")
count = Category.objects.count()
print(f"现有分类数量: {count}")

if count > 0:
    print("\n分类列表:")
    for cat in Category.objects.all():
        print(f"ID: {cat.id}, 名称: {cat.name}, 描述: {cat.description}")
else:
    print("\n没有找到任何分类数据")

print("\n=== 检查完成 ===")