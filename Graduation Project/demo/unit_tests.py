#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
校园二手交易平台单元测试脚本
包含模型测试、视图测试、API测试等详细单元测试
"""

import os
import sys
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')

import django
django.setup()

from marketplace.models import (
    Product, Category, Transaction, Message, Review, 
    TwoFactorAuth, SecurityLog, UserBehavior, Favorite,
    Knowledge, UserPreference, RecommendationLog, AbnormalBehavior
)
from marketplace.security import security_manager
from marketplace.recommendation import recommendation_engine


class ModelTests(TestCase):
    """模型单元测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        self.category = Category.objects.create(
            name='测试分类',
            description='测试分类描述'
        )
    
    def test_user_model(self):
        """测试用户模型"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpassword'))
    
    def test_category_model(self):
        """测试分类模型"""
        self.assertEqual(self.category.name, '测试分类')
        self.assertEqual(self.category.description, '测试分类描述')
        self.assertEqual(str(self.category), '测试分类')
    
    def test_product_model(self):
        """测试商品模型"""
        product = Product.objects.create(
            name='测试商品',
            description='测试商品描述',
            price=100.0,
            category=self.category,
            seller=self.user
        )
        
        self.assertEqual(product.name, '测试商品')
        self.assertEqual(product.price, 100.0)
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.seller, self.user)
        self.assertEqual(str(product), '测试商品')
    
    def test_transaction_model(self):
        """测试交易模型"""
        product = Product.objects.create(
            name='交易测试商品',
            description='交易测试商品描述',
            price=80.0,
            category=self.category,
            seller=self.user
        )
        
        buyer = User.objects.create_user(username='buyer', password='test123')
        
        transaction = Transaction.objects.create(
            product=product,
            buyer=buyer,
            seller=self.user,
            status='pending'
        )
        
        self.assertEqual(transaction.product, product)
        self.assertEqual(transaction.buyer, buyer)
        self.assertEqual(transaction.seller, self.user)
        self.assertEqual(transaction.status, 'pending')
    
    def test_message_model(self):
        """测试消息模型"""
        receiver = User.objects.create_user(username='receiver', password='test123')
        
        message = Message.objects.create(
            sender=self.user,
            receiver=receiver,
            content='测试消息内容',
            is_read=False
        )
        
        self.assertEqual(message.sender, self.user)
        self.assertEqual(message.receiver, receiver)
        self.assertEqual(message.content, '测试消息内容')
        self.assertFalse(message.is_read)
    
    def test_review_model(self):
        """测试评价模型"""
        product = Product.objects.create(
            name='评价测试商品',
            description='评价测试商品描述',
            price=60.0,
            category=self.category,
            seller=self.user
        )
        
        buyer = User.objects.create_user(username='reviewer', password='test123')
        
        transaction = Transaction.objects.create(
            product=product,
            buyer=buyer,
            seller=self.user,
            status='completed'
        )
        
        review = Review.objects.create(
            transaction=transaction,
            reviewer=buyer,
            rating=5,
            comment='非常好的商品'
        )
        
        self.assertEqual(review.transaction, transaction)
        self.assertEqual(review.reviewer, buyer)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, '非常好的商品')
    
    def test_two_factor_auth_model(self):
        """测试双因素认证模型"""
        two_factor = TwoFactorAuth.objects.create(
            user=self.user,
            secret_key='test_secret_key',
            is_enabled=False
        )
        
        self.assertEqual(two_factor.user, self.user)
        self.assertEqual(two_factor.secret_key, 'test_secret_key')
        self.assertFalse(two_factor.is_enabled)
    
    def test_security_log_model(self):
        """测试安全日志模型"""
        log = SecurityLog.objects.create(
            user=self.user,
            log_type='login',
            ip_address='127.0.0.1',
            user_agent='test user agent',
            details='测试登录',
            is_successful=True
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.log_type, 'login')
        self.assertEqual(log.ip_address, '127.0.0.1')
        self.assertEqual(log.details, '测试登录')
        self.assertTrue(log.is_successful)
    
    def test_user_behavior_model(self):
        """测试用户行为模型"""
        behavior = UserBehavior.objects.create(
            user=self.user,
            behavior_type='view_product',
            target_id=1,
            target_type='product',
            ip_address='127.0.0.1',
            user_agent='test user agent'
        )
        
        self.assertEqual(behavior.user, self.user)
        self.assertEqual(behavior.behavior_type, 'view_product')
        self.assertEqual(behavior.target_id, 1)
        self.assertEqual(behavior.target_type, 'product')
    
    def test_favorite_model(self):
        """测试收藏夹模型"""
        product = Product.objects.create(
            name='收藏测试商品',
            description='收藏测试商品描述',
            price=50.0,
            category=self.category,
            seller=self.user
        )
        
        favorite = Favorite.objects.create(
            user=self.user,
            product=product
        )
        
        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.product, product)


class SecurityModuleTests(TestCase):
    """安全模块单元测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='security_test_user',
            password='testpassword'
        )
    
    def test_generate_2fa_secret(self):
        """测试生成2FA密钥"""
        result = security_manager.generate_2fa_secret(self.user)
        
        self.assertIn('secret', result)
        self.assertIn('qr_code_url', result)
        self.assertIn('recovery_codes', result)
        self.assertEqual(len(result['recovery_codes']), 10)
        
        # 验证双因素认证记录是否创建
        two_factor = TwoFactorAuth.objects.get(user=self.user)
        self.assertEqual(two_factor.secret_key, result['secret'])
        self.assertFalse(two_factor.is_enabled)
    
    def test_security_logging(self):
        """测试安全日志记录"""
        # 记录安全事件
        security_manager.log_security_event(
            user=self.user,
            log_type='login',
            ip_address='127.0.0.1',
            user_agent='test user agent',
            details='测试登录',
            is_successful=True
        )
        
        # 检查日志是否创建
        logs = SecurityLog.objects.filter(user=self.user)
        self.assertEqual(logs.count(), 1)
        log = logs.first()
        self.assertEqual(log.log_type, 'login')
        self.assertEqual(log.ip_address, '127.0.0.1')
        self.assertEqual(log.details, '测试登录')
        self.assertTrue(log.is_successful)
    
    def test_data_encryption(self):
        """测试数据加密"""
        test_data = '测试加密数据'
        
        # 加密数据
        encrypted = security_manager.encrypt_data(test_data)
        self.assertIn('encrypted_value', encrypted)
        self.assertIn('iv', encrypted)
        
        # 解密数据
        decrypted = security_manager.decrypt_data(
            encrypted['encrypted_value'],
            encrypted['iv']
        )
        self.assertEqual(decrypted, test_data)
    
    def test_security_summary(self):
        """测试安全摘要"""
        # 获取安全摘要
        summary = security_manager.get_security_summary(self.user)
        
        # 检查摘要数据
        self.assertIn('two_factor_enabled', summary)
        self.assertIn('recent_logs', summary)
        self.assertIn('suspicious_count', summary)
        self.assertFalse(summary['two_factor_enabled'])
        self.assertEqual(summary['suspicious_count'], 0)


class RecommendationModuleTests(TestCase):
    """推荐模块单元测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='recommendation_test_user',
            password='testpassword'
        )
        
        self.category = Category.objects.create(name='推荐测试分类')
        
        # 创建测试商品
        self.products = []
        for i in range(5):
            product = Product.objects.create(
                name=f'推荐测试商品{i}',
                description=f'推荐测试商品描述{i}',
                price=100.0 + i * 10,
                category=self.category,
                seller=self.user
            )
            self.products.append(product)
    
    def test_recommendation_engine_initialization(self):
        """测试推荐引擎初始化"""
        # 推荐引擎应该能够正常初始化
        self.assertIsNotNone(recommendation_engine)
    
    def test_user_preference_creation(self):
        """测试用户偏好创建"""
        # 创建用户偏好
        preference = UserPreference.objects.create(
            user=self.user,
            preference_type='category',
            preference_value=str(self.category.id),
            weight=0.8
        )
        
        self.assertEqual(preference.user, self.user)
        self.assertEqual(preference.preference_type, 'category')
        self.assertEqual(preference.preference_value, str(self.category.id))
        self.assertEqual(preference.weight, 0.8)
    
    def test_recommendation_log_creation(self):
        """测试推荐日志创建"""
        # 创建推荐日志
        log = RecommendationLog.objects.create(
            user=self.user,
            recommendation_type='similar_products',
            target_id=self.products[0].id,
            target_type='product',
            success_rate=0.75
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.recommendation_type, 'similar_products')
        self.assertEqual(log.target_id, self.products[0].id)
        self.assertEqual(log.target_type, 'product')
        self.assertEqual(log.success_rate, 0.75)


class ViewTests(TestCase):
    """视图单元测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='view_test_user',
            password='testpassword'
        )
        self.category = Category.objects.create(name='视图测试分类')
    
    def test_home_view(self):
        """测试首页视图"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '校园二手交易平台')
    
    def test_product_list_view(self):
        """测试商品列表视图"""
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_product_detail_view(self):
        """测试商品详情视图"""
        product = Product.objects.create(
            name='视图测试商品',
            description='视图测试商品描述',
            price=100.0,
            category=self.category,
            seller=self.user
        )
        
        response = self.client.get(reverse('product_detail', args=[product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '视图测试商品')
    
    def test_search_view(self):
        """测试搜索视图"""
        response = self.client.get(reverse('search') + '?q=测试')
        self.assertEqual(response.status_code, 200)
    
    def test_user_profile_view(self):
        """测试用户个人资料视图"""
        # 需要登录才能访问
        self.client.login(username='view_test_user', password='testpassword')
        response = self.client.get(reverse('user_profile'))
        self.assertEqual(response.status_code, 200)


class APITests(TestCase):
    """API单元测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='api_test_user',
            password='testpassword'
        )
        self.category = Category.objects.create(name='API测试分类')
    
    def test_product_api_list(self):
        """测试商品API列表"""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)
    
    def test_category_api_list(self):
        """测试分类API列表"""
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, 200)
    
    def test_user_api_profile(self):
        """测试用户API个人资料"""
        # 需要认证
        self.client.login(username='api_test_user', password='testpassword')
        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)


def run_all_unit_tests():
    """运行所有单元测试"""
    import unittest
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        ModelTests,
        SecurityModuleTests,
        RecommendationModuleTests,
        ViewTests,
        APITests
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 生成测试报告
    generate_unit_test_report(result)


def generate_unit_test_report(result):
    """生成单元测试报告"""
    report_file = 'unit_test_report.txt'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("校园二手交易平台单元测试报告\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"测试运行时间: {result.testsRun}\n")
        f.write(f"失败测试数: {len(result.failures)}\n")
        f.write(f"错误测试数: {len(result.errors)}\n")
        f.write(f"跳过测试数: {len(result.skipped)}\n\n")
        
        if result.failures:
            f.write("失败测试详情:\n")
            for test, traceback in result.failures:
                f.write(f"  - {test}: {traceback}\n")
        
        if result.errors:
            f.write("错误测试详情:\n")
            for test, traceback in result.errors:
                f.write(f"  - {test}: {traceback}\n")
        
        f.write("\n测试总结:\n")
        if result.wasSuccessful():
            f.write("所有单元测试通过，代码质量良好。\n")
        else:
            f.write("部分单元测试失败，请检查相关代码。\n")
    
    print(f"单元测试报告已生成: {report_file}")


if __name__ == "__main__":
    print("校园二手交易平台单元测试")
    print("=" * 50)
    
    run_all_unit_tests()