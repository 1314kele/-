#!/usr/bin/env python
"""创建管理员用户"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# 检查是否已存在管理员
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@campus.edu',
        password='admin123'
    )
    print("✅ 管理员用户创建成功！")
    print("\n管理员信息：")
    print("  用户名: admin")
    print("  邮箱: admin@campus.edu")
    print("  密码: admin123")
else:
    print("管理员用户已存在！")
    user = User.objects.get(username='admin')
    print("\n管理员信息：")
    print(f"  用户名: {user.username}")
    print(f"  邮箱: {user.email}")
    print("  密码: admin123 (如果忘记密码，请使用 python manage.py changepassword admin)")
