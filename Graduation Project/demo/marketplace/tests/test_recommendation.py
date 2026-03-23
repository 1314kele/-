from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Category, Product, UserPreference, RecommendationLog
from ..recommendation import recommendation_system

class RecommendationTest(TestCase):
    """推荐系统测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        
        # 创建测试分类
        self.category1 = Category.objects.create(name='电子产品')
        self.category2 = Category.objects.create(name='书籍')
        
        # 创建测试商品
        self.product1 = Product.objects.create(
            title='测试手机',
            description='测试手机描述',
            price=1000.00,
            category=self.category1,
            seller=self.user,
            condition='good',
            status='available',
            location='测试地点',
            contact_info='测试联系方式'
        )
        
        self.product2 = Product.objects.create(
            title='测试书籍',
            description='测试书籍描述',
            price=50.00,
            category=self.category2,
            seller=self.user,
            condition='good',
            status='available',
            location='测试地点',
            contact_info='测试联系方式'
        )
    
    def test_user_preference_update(self):
        """测试用户偏好更新"""
        # 更新用户偏好（没有行为数据，返回True但没有创建偏好）
        result = recommendation_system.update_user_preferences(self.user.id)
        self.assertTrue(result)
        
        # 检查偏好是否创建（没有行为数据，应该没有偏好）
        preferences = UserPreference.objects.filter(user=self.user)
        self.assertFalse(preferences.exists())
    
    def test_collaborative_filtering(self):
        """测试协同过滤推荐"""
        # 获取协同过滤推荐
        recommendations = recommendation_system.collaborative_filtering(self.user.id, top_n=5)
        # 应该返回空列表（没有足够的行为数据）
        self.assertIsInstance(recommendations, list)
    
    def test_content_based(self):
        """测试内容推荐"""
        # 获取内容推荐
        recommendations = recommendation_system.content_based(self.user.id, top_n=5)
        # 应该返回热门商品
        self.assertIsInstance(recommendations, list)
    
    def test_social_factor(self):
        """测试社交因子推荐"""
        # 获取社交因子推荐
        recommendations = recommendation_system.social_factor(self.user.id, top_n=5)
        # 应该返回空列表（没有社交数据）
        self.assertIsInstance(recommendations, list)
    
    def test_hybrid_recommendation(self):
        """测试混合推荐"""
        # 获取混合推荐
        recommendations = recommendation_system.hybrid_recommendation(self.user.id, top_n=5)
        # 应该返回推荐结果
        self.assertIsInstance(recommendations, list)
    
    def test_recommendation_log(self):
        """测试推荐日志"""
        # 获取推荐
        recommendation_system.get_recommendations(self.user.id, top_n=2, strategy='hybrid')
        
        # 检查推荐日志是否创建
        logs = RecommendationLog.objects.filter(user=self.user)
        self.assertTrue(logs.exists())
        # 混合推荐会记录所有推荐的商品，包括重复的
        self.assertGreater(logs.count(), 0)