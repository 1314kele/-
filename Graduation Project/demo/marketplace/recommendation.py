import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Count, Q, F
from .models import UserBehavior, Product, User, Category, UserPreference, ProductSimilarity, RecommendationLog
import time
import logging

logger = logging.getLogger(__name__)

class RecommendationSystem:
    """推荐系统类"""
    
    def __init__(self):
        """初始化推荐系统"""
        pass
    
    def get_recommendations(self, user_id, top_n=10, strategy='hybrid'):
        """获取推荐商品"""
        if strategy == 'collaborative':
            return self.collaborative_filtering(user_id, top_n)
        elif strategy == 'content':
            return self.content_based(user_id, top_n)
        elif strategy == 'social':
            return self.social_factor(user_id, top_n)
        elif strategy == 'hybrid':
            return self.hybrid_recommendation(user_id, top_n)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def collaborative_filtering(self, user_id, top_n=10):
        """协同过滤推荐"""
        try:
            # 获取用户历史行为
            user_behaviors = UserBehavior.objects.filter(user_id=user_id)
            viewed_product_ids = user_behaviors.filter(action_type__in=['browse', 'click', 'transaction']).values_list('action_data', flat=True)
            
            # 获取具有相似行为的用户
            similar_users = UserBehavior.objects.filter(
                action_type__in=['browse', 'click', 'transaction'],
                action_data__in=viewed_product_ids
            ).exclude(user_id=user_id).values('user_id').annotate(
                similarity=Count('action_data', distinct=True)
            ).order_by('-similarity')[:20]
            
            similar_user_ids = [u['user_id'] for u in similar_users]
            
            # 获取相似用户喜欢的商品
            recommended_products = Product.objects.filter(
                id__in=UserBehavior.objects.filter(
                    user_id__in=similar_user_ids,
                    action_type__in=['click', 'transaction']
                ).values_list('action_data', flat=True)
            ).exclude(id__in=viewed_product_ids).annotate(
                score=Count('id')
            ).order_by('-score')[:top_n]
            
            # 记录推荐日志
            for product in recommended_products:
                RecommendationLog.objects.create(
                    user_id=user_id,
                    product=product,
                    recommendation_type='collaborative',
                    score=product.score
                )
            
            return list(recommended_products)
            
        except Exception as e:
            logger.error(f"Collaborative filtering error: {str(e)}")
            return []
    
    def content_based(self, user_id, top_n=10):
        """内容推荐"""
        try:
            # 获取用户偏好
            user_preferences = UserPreference.objects.filter(user_id=user_id).order_by('-preference_score')
            
            if not user_preferences:
                # 如果没有偏好数据，基于浏览历史
                viewed_categories = UserBehavior.objects.filter(
                    user_id=user_id,
                    action_type__in=['browse', 'click']
                ).values_list('action_data', flat=True)
                
                if viewed_categories:
                    recommended_products = Product.objects.filter(
                        category_id__in=viewed_categories
                    ).order_by('-create_time')[:top_n]
                else:
                    # 冷启动策略：推荐热门商品
                    recommended_products = Product.objects.order_by('-views')[:top_n]
            else:
                # 基于偏好推荐
                preferred_category_ids = [p.category_id for p in user_preferences[:5]]
                recommended_products = Product.objects.filter(
                    category_id__in=preferred_category_ids
                ).order_by('-create_time')[:top_n]
            
            # 记录推荐日志
            for product in recommended_products:
                RecommendationLog.objects.create(
                    user_id=user_id,
                    product=product,
                    recommendation_type='content',
                    score=1.0
                )
            
            return list(recommended_products)
            
        except Exception as e:
            logger.error(f"Content based error: {str(e)}")
            return []
    
    def social_factor(self, user_id, top_n=10):
        """社交因子推荐"""
        try:
            # 模拟社交关系（实际项目中需要社交关系模型）
            # 这里简单返回空列表，因为没有社交关系数据
            recommended_products = []
            
            # 记录推荐日志（这里没有商品，所以不记录）
            
            return recommended_products
            
        except Exception as e:
            logger.error(f"Social factor error: {str(e)}")
            return []
    
    def hybrid_recommendation(self, user_id, top_n=10):
        """混合推荐"""
        try:
            # 获取各策略的推荐结果
            collaborative_results = self.collaborative_filtering(user_id, top_n * 2)
            content_results = self.content_based(user_id, top_n * 2)
            social_results = self.social_factor(user_id, top_n * 2)
            
            # 合并结果并去重
            product_scores = {}
            
            # 协同过滤结果权重
            for i, product in enumerate(collaborative_results):
                product_scores[product.id] = product_scores.get(product.id, 0) + (1.0 / (i + 1)) * 0.4
            
            # 内容推荐结果权重
            for i, product in enumerate(content_results):
                product_scores[product.id] = product_scores.get(product.id, 0) + (1.0 / (i + 1)) * 0.3
            
            # 社交因子结果权重
            for i, product in enumerate(social_results):
                product_scores[product.id] = product_scores.get(product.id, 0) + (1.0 / (i + 1)) * 0.3
            
            # 排序并获取Top N
            sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
            recommended_product_ids = [p[0] for p in sorted_products]
            recommended_products = list(Product.objects.filter(id__in=recommended_product_ids))
            
            # 记录推荐日志
            for product_id, score in sorted_products:
                try:
                    product = Product.objects.get(id=product_id)
                    RecommendationLog.objects.create(
                        user_id=user_id,
                        product=product,
                        recommendation_type='hybrid',
                        score=score
                    )
                except:
                    pass
            
            return recommended_products
            
        except Exception as e:
            logger.error(f"Hybrid recommendation error: {str(e)}")
            return []
    
    def update_user_preferences(self, user_id):
        """更新用户偏好"""
        try:
            # 分析用户行为
            behaviors = UserBehavior.objects.filter(user_id=user_id)
            
            # 计算各分类的偏好分数
            category_scores = {}
            for behavior in behaviors:
                if behavior.action_type == 'browse':
                    weight = 0.1
                elif behavior.action_type == 'click':
                    weight = 0.3
                elif behavior.action_type == 'favorite':
                    weight = 0.5
                elif behavior.action_type == 'transaction':
                    weight = 1.0
                else:
                    weight = 0.05
                
                # 假设action_data中存储了商品ID
                try:
                    product = Product.objects.get(id=behavior.action_data)
                    category_id = product.category_id
                    category_scores[category_id] = category_scores.get(category_id, 0) + weight
                except:
                    pass
            
            # 更新用户偏好
            for category_id, score in category_scores.items():
                UserPreference.objects.update_or_create(
                    user_id=user_id,
                    category_id=category_id,
                    defaults={'preference_score': score}
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Update user preferences error: {str(e)}")
            return False
    
    def update_product_similarity(self):
        """更新商品相似度"""
        try:
            # 获取所有商品
            products = Product.objects.all()
            
            for i, product1 in enumerate(products):
                for j, product2 in enumerate(products):
                    if i >= j:
                        continue
                    
                    # 计算相似度（基于分类、价格等）
                    similarity = 0.0
                    
                    # 分类相似度
                    if product1.category == product2.category:
                        similarity += 0.5
                    
                    # 价格相似度
                    price_diff = abs(product1.price - product2.price) / max(product1.price, product2.price, 1)
                    similarity += (1 - price_diff) * 0.3
                    
                    # 标题相似度（简单实现）
                    common_words = len(set(product1.name.split()) & set(product2.name.split()))
                    total_words = len(set(product1.name.split()) | set(product2.name.split()))
                    if total_words > 0:
                        similarity += (common_words / total_words) * 0.2
                    
                    # 保存相似度
                    if similarity > 0.1:
                        ProductSimilarity.objects.update_or_create(
                            product1=product1,
                            product2=product2,
                            defaults={'similarity_score': similarity}
                        )
            
        except Exception as e:
            logger.error(f"Update product similarity error: {str(e)}")

# 全局推荐系统实例
recommendation_system = RecommendationSystem()