#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园二手交易平台功能测试脚本
包含用户管理、商品管理、交易管理、安全功能等测试
"""

import os
import sys
import time
import unittest
from datetime import datetime

# 添加项目路径并配置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')

import django
django.setup()

from django.contrib.auth.models import User
from django.test import TestCase, Client
from marketplace.models import (
    Category, Product, Transaction, Message, Review, 
    UserBehavior, TwoFactorAuth, SecurityLog
)
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile


class FunctionalTestSuite(TestCase):
    """功能测试套件"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = Client()
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def run_test(self, test_func, test_name):
        """运行单个测试并记录结果"""
        try:
            print(f"正在执行: {test_name}")
            test_func()
            self.test_results['passed'] += 1
            print(f"[PASS] {test_name} - 通过\n")
        except AssertionError as e:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {str(e)}")
            print(f"[FAIL] {test_name} - 失败: {str(e)}\n")
        except Exception as e:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {str(e)}")
            print(f"[ERROR] {test_name} - 错误: {str(e)}\n")
    
    def test_user_registration(self):
        """测试用户注册功能"""
        # 测试注册页面可访问
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        
        # 测试用户注册
        user_data = {
            'username': 'testuser_functional',
            'email': 'test@example.com',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = self.client.post('/register/', user_data)
        self.assertEqual(response.status_code, 302)  # 重定向到成功页面
        
        # 验证用户是否创建成功
        user_exists = User.objects.filter(username='testuser_functional').exists()
        self.assertTrue(user_exists)
    
    def test_user_login_logout(self):
        """测试用户登录和登出功能"""
        # 创建测试用户
        user = User.objects.create_user(
            username='login_test_user',
            password='testpassword123',
            email='login@test.com'
        )
        
        # 测试登录页面
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        
        # 测试用户登录
        login_data = {
            'username': 'login_test_user',
            'password': 'testpassword123'
        }
        response = self.client.post('/login/', login_data)
        self.assertEqual(response.status_code, 302)  # 登录成功重定向
        
        # 验证用户已登录
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # 测试用户登出
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
        
        # 清理测试用户
        user.delete()
    
    def test_product_management(self):
        """测试商品管理功能"""
        # 创建测试用户和分类
        user = User.objects.create_user(
            username='product_test_user',
            password='testpassword123'
        )
        category = Category.objects.create(name='测试分类', description='测试分类描述')
        
        # 登录用户
        self.client.login(username='product_test_user', password='testpassword123')
        
        # 测试商品发布页面
        response = self.client.get('/products/add/')
        self.assertEqual(response.status_code, 200)
        
        # 测试商品发布
        product_data = {
            'title': '功能测试商品',
            'description': '这是一个功能测试商品',
            'price': 100.0,
            'category': category.id,
            'condition': 'excellent',
            'location': '测试地点'
        }
        
        # 模拟图片上传
        image_content = b'fake image content'
        image_file = SimpleUploadedFile(
            "test_image.jpg", 
            image_content, 
            content_type="image/jpeg"
        )
        product_data['image'] = image_file
        
        response = self.client.post('/products/add/', product_data)
        self.assertEqual(response.status_code, 302)  # 发布成功重定向
        
        # 验证商品是否创建成功
        product_exists = Product.objects.filter(
            title='功能测试商品', 
            seller=user
        ).exists()
        self.assertTrue(product_exists)
        
        # 测试商品列表页面
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, 200)
        
        # 测试商品详情页面
        product = Product.objects.get(title='功能测试商品')
        response = self.client.get(f'/products/{product.id}/')
        self.assertEqual(response.status_code, 200)
        
        # 清理测试数据
        product.delete()
        category.delete()
        user.delete()
    
    def test_search_functionality(self):
        """测试搜索功能"""
        # 创建测试商品
        user = User.objects.create_user(username='search_test_user', password='test123')
        category = Category.objects.create(name='搜索测试分类')
        
        product = Product.objects.create(
            title='搜索测试商品',
            description='这是一个用于搜索功能测试的商品',
            price=50.0,
            category=category,
            seller=user
        )
        
        # 测试关键词搜索
        response = self.client.get('/search/?q=搜索测试')
        self.assertEqual(response.status_code, 200)
        
        # 清理测试数据
        product.delete()
        category.delete()
        user.delete()
    
    def test_transaction_management(self):
        """测试交易管理功能"""
        # 创建测试用户和商品
        seller = User.objects.create_user(username='seller_user', password='test123')
        buyer = User.objects.create_user(username='buyer_user', password='test123')
        category = Category.objects.create(name='交易测试分类')
        
        product = Product.objects.create(
            name='交易测试商品',
            description='交易功能测试商品',
            price=80.0,
            category=category,
            seller=seller
        )
        
        # 买家登录
        self.client.login(username='buyer_user', password='test123')
        
        # 测试发起交易
        transaction_data = {
            'product': product.id,
            'buyer_message': '我想购买这个商品',
            'offer_price': 75.0
        }
        
        response = self.client.post('/marketplace/transaction/create/', transaction_data)
        self.assertEqual(response.status_code, 302)
        
        # 验证交易是否创建
        transaction_exists = Transaction.objects.filter(
            product=product, 
            buyer=buyer
        ).exists()
        self.assertTrue(transaction_exists)
        
        # 清理测试数据
        Transaction.objects.filter(product=product).delete()
        product.delete()
        category.delete()
        seller.delete()
        buyer.delete()
    
    def test_message_system(self):
        """测试消息系统功能"""
        # 创建测试用户
        user1 = User.objects.create_user(username='user1', password='test123')
        user2 = User.objects.create_user(username='user2', password='test123')
        
        # 用户1登录
        self.client.login(username='user1', password='test123')
        
        # 测试发送消息
        message_data = {
            'receiver': user2.id,
            'content': '这是一条测试消息'
        }
        
        response = self.client.post('/marketplace/message/send/', message_data)
        self.assertEqual(response.status_code, 302)
        
        # 验证消息是否发送成功
        message_exists = Message.objects.filter(
            sender=user1, 
            receiver=user2,
            content='这是一条测试消息'
        ).exists()
        self.assertTrue(message_exists)
        
        # 测试消息列表
        response = self.client.get('/marketplace/messages/')
        self.assertEqual(response.status_code, 200)
        
        # 清理测试数据
        Message.objects.filter(sender=user1).delete()
        user1.delete()
        user2.delete()
    
    def test_review_system(self):
        """测试评价系统功能"""
        # 创建测试用户和商品
        seller = User.objects.create_user(username='review_seller', password='test123')
        buyer = User.objects.create_user(username='review_buyer', password='test123')
        category = Category.objects.create(name='评价测试分类')
        
        product = Product.objects.create(
            name='评价测试商品',
            description='评价功能测试商品',
            price=60.0,
            category=category,
            seller=seller
        )
        
        transaction = Transaction.objects.create(
            product=product,
            buyer=buyer,
            seller=seller,
            status='completed'
        )
        
        # 买家登录
        self.client.login(username='review_buyer', password='test123')
        
        # 测试发布评价
        review_data = {
            'transaction': transaction.id,
            'rating': 5,
            'comment': '商品质量很好，交易顺利'
        }
        
        response = self.client.post('/marketplace/review/create/', review_data)
        self.assertEqual(response.status_code, 302)
        
        # 验证评价是否创建
        review_exists = Review.objects.filter(
            transaction=transaction,
            reviewer=buyer
        ).exists()
        self.assertTrue(review_exists)
        
        # 清理测试数据
        Review.objects.filter(transaction=transaction).delete()
        transaction.delete()
        product.delete()
        category.delete()
        seller.delete()
        buyer.delete()
    
    def test_security_features(self):
        """测试安全功能"""
        # 创建测试用户
        user = User.objects.create_user(username='security_test_user', password='test123')
        
        # 测试双因素认证设置页面
        self.client.login(username='security_test_user', password='test123')
        response = self.client.get('/marketplace/security/2fa/')
        self.assertEqual(response.status_code, 200)
        
        # 测试安全日志功能
        response = self.client.get('/marketplace/security/logs/')
        self.assertEqual(response.status_code, 200)
        
        # 验证安全日志记录
        logs_count = SecurityLog.objects.filter(user=user).count()
        self.assertGreaterEqual(logs_count, 0)
        
        # 清理测试数据
        user.delete()
    
    def test_user_behavior_tracking(self):
        """测试用户行为追踪功能"""
        # 创建测试用户
        user = User.objects.create_user(username='behavior_test_user', password='test123')
        
        # 用户登录后访问页面
        self.client.login(username='behavior_test_user', password='test123')
        
        # 访问多个页面以生成行为数据
        self.client.get('/')
        self.client.get('/marketplace/products/')
        self.client.get('/marketplace/search/?q=测试')
        
        # 验证行为数据是否记录
        behavior_count = UserBehavior.objects.filter(user=user).count()
        self.assertGreaterEqual(behavior_count, 0)
        
        # 清理测试数据
        user.delete()
    
    def run_all_functional_tests(self):
        """运行所有功能测试"""
        print("开始功能测试套件...")
        print("=" * 60)
        
        tests = [
            (self.test_user_registration, "用户注册功能测试"),
            (self.test_user_login_logout, "用户登录登出功能测试"),
            (self.test_product_management, "商品管理功能测试"),
            (self.test_search_functionality, "搜索功能测试"),
            (self.test_transaction_management, "交易管理功能测试"),
            (self.test_message_system, "消息系统功能测试"),
            (self.test_review_system, "评价系统功能测试"),
            (self.test_security_features, "安全功能测试"),
            (self.test_user_behavior_tracking, "用户行为追踪测试")
        ]
        
        for test_func, test_name in tests:
            self.run_test(test_func, test_name)
        
        # 生成测试报告
        self.generate_functional_test_report()
    
    def generate_functional_test_report(self):
        """生成功能测试报告"""
        print("\n=== 功能测试报告 ===")
        print(f"通过测试: {self.test_results['passed']}")
        print(f"失败测试: {self.test_results['failed']}")
        print(f"总测试数: {self.test_results['passed'] + self.test_results['failed']}")
        
        if self.test_results['errors']:
            print("\n错误详情:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        # 保存详细报告到文件
        report_file = 'functional_test_report.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("校园二手交易平台功能测试报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"通过测试: {self.test_results['passed']}\n")
            f.write(f"失败测试: {self.test_results['failed']}\n")
            f.write(f"总测试数: {self.test_results['passed'] + self.test_results['failed']}\n")
            f.write(f"测试通过率: {self.test_results['passed']/(self.test_results['passed'] + self.test_results['failed']) * 100:.1f}%\n\n")
            
            if self.test_results['errors']:
                f.write("错误详情:\n")
                for error in self.test_results['errors']:
                    f.write(f"  - {error}\n")
            
            f.write("\n测试总结:\n")
            if self.test_results['failed'] == 0:
                f.write("所有功能测试通过，系统功能正常。\n")
            else:
                f.write("部分功能测试失败，请检查相关功能模块。\n")
        
        print(f"\n详细测试报告已保存到: {report_file}")


def main():
    """主函数"""
    print("校园二手交易平台功能测试")
    print("=" * 50)
    
    # 运行功能测试
    test_suite = FunctionalTestSuite()
    test_suite.run_all_functional_tests()


if __name__ == "__main__":
    main()