#!/usr/bin/env python
"""检查管理员用户"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 50)
print("管理员用户信息")
print("=" * 50)

admin_users = User.objects.filter(is_superuser=True)

if admin_users.exists():
    for user in admin_users:
        print(f"\n用户名: {user.username}")
        print(f"邮箱: {user.email}")
        print(f"超级用户: {'是' if user.is_superuser else '否'}")
        print(f"工作人员: {'是' if user.is_staff else '否'}")
        print(f"状态: {'激活' if user.is_active else '未激活'}")
else:
    print("\n没有找到管理员用户！")
    print("\n建议创建一个管理员用户：")
    print("  python manage.py createsuperuser")

print("\n" + "=" * 50)
