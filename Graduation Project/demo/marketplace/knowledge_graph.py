"""
校园二手交易领域知识图谱模块
构建商品、用户、行为、分类、评价、交易规则的知识关联体系
"""
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Category, Product, Favorite, Review, UserBehavior, Knowledge


class KnowledgeGraph:
    """校园二手交易知识图谱"""
    
    @staticmethod
    def build_product_relationship(product):
        """
        构建商品的知识关系
        包括：分类、用户、行为、评价等关联
        """
        relationships = {
            'product': product,
            'category': product.category,
            'seller': product.seller,
            'related_products': [],
            'favorites': [],
            'reviews': [],
            'browse_behaviors': []
        }
        
        # 获取同类商品（基于分类）
        related_products = Product.objects.filter(
            category=product.category,
            status='available'
        ).exclude(id=product.id)[:5]
        relationships['related_products'] = list(related_products)
        
        # 获取收藏该商品的用户
        favorites = Favorite.objects.filter(product=product)
        relationships['favorites'] = list(favorites)
        
        # 获取该商品的评价
        reviews = Review.objects.filter(product=product)
        relationships['reviews'] = list(reviews)
        
        # 获取浏览该商品的行为记录
        browse_behaviors = UserBehavior.objects.filter(
            action_type='browse',
            action_data__contains=str(product.id)
        )[:20]
        relationships['browse_behaviors'] = list(browse_behaviors)
        
        return relationships
    
    @staticmethod
    def get_knowledge_rules():
        """
        从知识库获取推荐规则和安全规则
        """
        knowledge_rules = {
            'recommendation_rules': [],
            'security_rules': []
        }
        
        # 获取交易技巧作为推荐规则
        tip_knowledge = Knowledge.objects.filter(knowledge_type='tip')
        for knowledge in tip_knowledge:
            knowledge_rules['recommendation_rules'].append({
                'title': knowledge.title,
                'content': knowledge.content,
                'keywords': knowledge.keywords.split(',') if knowledge.keywords else []
            })
        
        # 获取平台规则作为安全规则
        rule_knowledge = Knowledge.objects.filter(knowledge_type='rule')
        for knowledge in rule_knowledge:
            knowledge_rules['security_rules'].append({
                'title': knowledge.title,
                'content': knowledge.content,
                'keywords': knowledge.keywords.split(',') if knowledge.keywords else []
            })
        
        return knowledge_rules


def calculate_product_similarity(product1, product2):
    """
    基于知识库计算两个商品的相似度
    使用：分类体系 + 关键词 + 商品属性 + 价格区间
    """
    similarity_score = 0.0
    
    # 1. 分类相似度（权重 30%）
    if product1.category == product2.category:
        similarity_score += 30
    elif product1.category.parent == product2.category.parent if hasattr(product1.category, 'parent') else False:
        similarity_score += 15
    
    # 2. 标题关键词相似度（权重 25%）
    keywords1 = set(product1.title.lower().split())
    keywords2 = set(product2.title.lower().split())
    intersection = keywords1 & keywords2
    union = keywords1 | keywords2
    if union:
        jaccard = len(intersection) / len(union)
        similarity_score += jaccard * 25
    
    # 3. 价格区间相似度（权重 20%）
    price_diff = abs(float(product1.price) - float(product2.price))
    max_price = max(float(product1.price), float(product2.price))
    if max_price > 0:
        price_similarity = max(0, 1 - price_diff / max_price)
        similarity_score += price_similarity * 20
    
    # 4. 商品状况相似度（权重 15%）
    if product1.condition == product2.condition:
        similarity_score += 15
    else:
        condition_order = ['new', 'like_new', 'good', 'fair', 'poor']
        idx1 = condition_order.index(product1.condition) if product1.condition in condition_order else 2
        idx2 = condition_order.index(product2.condition) if product2.condition in condition_order else 2
        condition_diff = abs(idx1 - idx2)
        similarity_score += max(0, 15 - condition_diff * 3)
    
    # 5. 浏览量热度相似度（权重 10%）
    views1 = product1.views or 0
    views2 = product2.views or 0
    max_views = max(views1, views2)
    if max_views > 0:
        views_similarity = 1 - abs(views1 - views2) / max_views
        similarity_score += views_similarity * 10
    
    return min(100, similarity_score)


def get_campus_period_factor():
    """
    计算校园周期性因子
    毕业季、开学季商品权重提升
    """
    now = datetime.now()
    month = now.month
    day = now.day
    
    period_factor = 1.0
    
    # 毕业季：5月-6月
    if 5 <= month <= 6:
        period_factor = 1.5
    
    # 开学季：8月底-9月底
    elif (month == 8 and day >= 20) or (month == 9 and day <= 30):
        period_factor = 1.5
    
    # 寒假前后：1月、2月
    elif month in [1, 2]:
        period_factor = 1.2
    
    # 暑假前后：7月、8月上旬
    elif month == 7 or (month == 8 and day < 20):
        period_factor = 1.2
    
    return period_factor


def get_campus_seasonal_categories():
    """
    获取当前校园季节相关的商品分类
    """
    now = datetime.now()
    month = now.month
    
    seasonal_categories = []
    
    # 毕业季： textbooks, electronics
    if 5 <= month <= 6:
        seasonal_categories.extend(['图书教材', '电子产品', '生活用品'])
    
    # 开学季： textbooks, dorm supplies
    elif (month == 8 and month >= 20) or month == 9:
        seasonal_categories.extend(['图书教材', '生活用品', '电子产品'])
    
    # 冬季： winter clothes, heaters
    elif month in [11, 12, 1, 2]:
        seasonal_categories.extend(['服装鞋帽', '生活用品'])
    
    # 夏季： summer clothes, coolers
    elif month in [6, 7, 8]:
        seasonal_categories.extend(['服装鞋帽', '运动户外', '生活用品'])
    
    return seasonal_categories
