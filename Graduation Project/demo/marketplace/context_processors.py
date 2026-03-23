"""
自定义上下文处理器
为所有模板提供全局数据
"""
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Category, Product, Favorite, Review, AbnormalBehavior, BehaviorReport
from .knowledge_graph import calculate_product_similarity, get_campus_period_factor, get_campus_seasonal_categories


def calculate_user_credit_score(user):
    """
    计算用户信用分数，用于推荐算法中的信用权重
    基于用户评价、异常行为、交易记录等多维度计算
    
    返回：0.0 - 1.0 的信用权重，1.0表示最高信用
    """
    if not user or not user.is_authenticated:
        return 0.5
    
    credit_score = 1.0
    
    # 1. 基于用户收到的评价计算
    received_reviews = Review.objects.filter(reviewed_user=user)
    if received_reviews.exists():
        avg_rating = received_reviews.aggregate(Avg('rating'))['rating__avg'] or 3.0
        # 评分从1-5映射到0-1
        rating_factor = avg_rating / 5.0
        credit_score *= (0.5 + 0.5 * rating_factor)
    
    # 2. 基于异常行为记录扣分
    recent_abnormal = AbnormalBehavior.objects.filter(
        user=user,
        detected_time__gte=timezone.now() - timedelta(days=30)
    ).count()
    if recent_abnormal > 0:
        # 每有一次异常行为，信用降低
        credit_score *= max(0.3, 1.0 - recent_abnormal * 0.2)
    
    # 3. 基于行为报告扣分
    recent_reports = BehaviorReport.objects.filter(
        user=user,
        report_time__gte=timezone.now() - timedelta(days=30),
        admin_status__in=['pending', 'processing']
    ).count()
    if recent_reports > 0:
        credit_score *= max(0.4, 1.0 - recent_reports * 0.3)
    
    # 4. 确保分数在合理范围内
    credit_score = max(0.1, min(1.0, credit_score))
    
    return credit_score


def global_categories(request):
    """
    为所有模板提供分类数据
    """
    return {
        'global_categories': Category.objects.all().order_by('name'),
    }


def global_user_stats(request):
    """
    为所有模板提供用户统计信息
    """
    if request.user.is_authenticated:
        return {
            'user_favorite_count': request.user.favorites.count() if hasattr(request.user, 'favorites') else 0,
            'user_message_count': request.user.received_messages.filter(is_read=False).count() if hasattr(request.user, 'received_messages') else 0,
        }
    return {}


def get_hot_recommendations(request):
    """
    基于多维度算法计算热门推荐商品
    
    算法维度：
    1. 浏览量 (30%) - 商品被查看的次数
    2. 收藏数 (25%) - 商品被收藏的次数
    3. 交易状态 (20%) - 可交易状态获得更高权重
    4. 时间衰减 (15%) - 新发布的商品获得更高权重
    5. 价格合理性 (10%) - 基于同类商品价格分布，价格越低得分越高
    
    返回前4个热门推荐商品
    """
    from django.db.models import Count, Case, When, Value, FloatField
    from django.db.models.functions import Now
    
    # 获取当前时间
    now = timezone.now()
    
    # 计算每个商品的收藏数
    products_with_favorites = Product.objects.annotate(
        favorite_count=Count('favorite', distinct=True)
    )
    
    # 获取所有可交易商品的价格分布（按分类分组）
    category_prices = {}
    for category in Category.objects.all():
        category_products = Product.objects.filter(
            category=category, 
            status='available'
        ).values_list('price', flat=True)
        
        if category_products.exists():
            prices = sorted(category_products)
            category_prices[category.id] = {
                'min': min(prices),
                'max': max(prices),
                'median': prices[len(prices) // 2],
                'q25': prices[len(prices) // 4] if len(prices) >= 4 else prices[0],
                'q75': prices[len(prices) * 3 // 4] if len(prices) >= 4 else prices[-1],
            }
    
    # 计算热门分数
    hot_products = []
    for product in products_with_favorites.filter(status='available')[:20]:
        # 1. 浏览量分数 (0-30分) - 归一化到0-30
        views_score = min(product.views / 10, 30) if product.views else 0
        
        # 2. 收藏数分数 (0-25分)
        favorite_score = min(product.favorite_count * 5, 25)
        
        # 3. 交易状态分数 (0-20分) - 可交易状态获得满分
        status_score = 20 if product.status == 'available' else 0
        
        # 4. 时间衰减分数 (0-15分) - 7天内发布的获得满分，之后线性衰减
        days_since_created = (now - product.created_at).days
        if days_since_created <= 7:
            time_score = 15
        elif days_since_created <= 30:
            time_score = 15 * (1 - (days_since_created - 7) / 23)
        else:
            time_score = 0
        
        # 5. 价格合理性分数 (0-10分) - 基于同类商品价格分布
        price = float(product.price)
        category_id = product.category.id
        
        if category_id in category_prices:
            price_data = category_prices[category_id]
            price_range = float(price_data['max']) - float(price_data['min'])
            
            if price_range == 0:
                # 同类商品价格相同
                price_score = 10
            else:
                # 计算价格在同类商品中的相对位置 (0-1之间)
                price_position = (price - float(price_data['min'])) / price_range
                
                # 价格越低，分数越高
                # 价格在下25%：10分
                # 价格在25%-50%：8分
                # 价格在50%-75%：5分
                # 价格在上25%：2分
                if price_position <= 0.25:
                    price_score = 10
                elif price_position <= 0.5:
                    price_score = 8
                elif price_position <= 0.75:
                    price_score = 5
                else:
                    price_score = 2
        else:
            # 没有同类商品数据，给予基础分数
            price_score = 5
        
        # 计算总分
        total_score = views_score + favorite_score + status_score + time_score + price_score
        
        hot_products.append({
            'product': product,
            'score': total_score,
            'views_score': views_score,
            'favorite_score': favorite_score,
            'status_score': status_score,
            'time_score': time_score,
            'price_score': price_score,
        })
    
    # 按分数排序，取前4个
    hot_products.sort(key=lambda x: x['score'], reverse=True)
    top_products = hot_products[:4]
    
    # 格式化推荐项
    recommendations = []
    for item in top_products:
        product = item['product']
        recommendations.append({
            'id': product.id,
            'title': product.title,
            'price': product.price,
            'image': product.image.url if product.image else None,
            'category': product.category.name,
            'views': product.views,
            'favorite_count': product.favorite_count,
            'score': round(item['score'], 2),
            'url': f'/products/{product.id}/',
        })
    
    return {
        'hot_recommendations': recommendations,
    }


def get_recommendations_for_user(request):
    """
    基于用户历史浏览数据、偏好设置及热门趋势算法的个性化推荐
    融合知识 + 行为 + 安全权重 + 校园周期的混合推荐
    
    算法逻辑：
    1. 如果用户已登录：
       - 分析用户浏览历史，找出最常浏览的商品分类
       - 分析用户收藏的商品
       - 基于用户偏好推荐相关商品
       - 引入用户信用权重：降低高风险用户商品的推荐权重
       - 基于知识库计算商品相似度
       - 引入校园周期性因子：毕业季、开学季权重提升
    2. 如果用户未登录：
       - 基于热门趋势推荐
       - 引入校园周期性因子
    3. 确保推荐商品与热门推荐不重复
    4. 生成推荐可解释性理由
    
    返回前4个个性化推荐商品，包含推荐理由
    """
    from django.db.models import Count
    
    # 获取校园周期性因子和季节性分类
    campus_period_factor = get_campus_period_factor()
    seasonal_categories = get_campus_seasonal_categories()
    
    # 存储已在热门推荐中的商品ID
    hot_product_ids = []
    if hasattr(request, 'hot_recommendations'):
        hot_product_ids = [item['id'] for item in request.hot_recommendations]
    else:
        # 如果hot_recommendations不存在，从热门推荐处理器获取
        hot_recs = get_hot_recommendations(request)
        hot_product_ids = [item['id'] for item in hot_recs.get('hot_recommendations', [])]
    
    recommended_products_with_scores = []
    
    # 获取当前用户的信用分数（用于推荐可解释性）
    current_user_credit = calculate_user_credit_score(request.user) if request.user.is_authenticated else 0.5
    
    # 获取用户最近浏览的商品，用于相似度计算
    recent_browsed_products = []
    if request.user.is_authenticated:
        from .models import UserBehavior
        recent_browse_behaviors = UserBehavior.objects.filter(
            user=request.user,
            action_type='browse',
            action_time__gte=timezone.now() - timedelta(days=7)
        ).order_by('-action_time')[:5]
        
        for behavior in recent_browse_behaviors:
            try:
                if behavior.action_data:
                    import json
                    data = json.loads(behavior.action_data)
                    if 'product_id' in data:
                        product = Product.objects.filter(id=data['product_id']).first()
                        if product:
                            recent_browsed_products.append(product)
            except:
                pass
    
    if request.user.is_authenticated:
        # 获取用户收藏的商品
        user_favorites = Favorite.objects.filter(user=request.user)
        favorite_product_ids = [fav.product.id for fav in user_favorites]
        favorite_products = [fav.product for fav in user_favorites]
        
        # 分析用户收藏的商品分类
        favorite_categories = Category.objects.filter(
            product__favorite__user=request.user
        ).annotate(
            product_count=Count('product')
        ).order_by('-product_count')
        
        # 获取用户偏好的分类
        preferred_category_ids = [cat.id for cat in favorite_categories[:3]]  # 取前3个偏好分类
        preferred_category_names = [cat.name for cat in favorite_categories[:3]]
        
        # 获取候选商品池
        candidate_products = Product.objects.filter(
            status='available'
        ).exclude(id__in=hot_product_ids + favorite_product_ids)
        
        # 先尝试从偏好分类和季节性分类中选择
        if preferred_category_ids:
            filtered_products = candidate_products.filter(
                Q(category_id__in=preferred_category_ids) | Q(category__name__in=seasonal_categories)
            )
        else:
            filtered_products = candidate_products.filter(
                Q(category__name__in=seasonal_categories)
            )
        
        # 如果过滤后的商品不足，回退到所有可用商品
        if filtered_products.count() < 4:
            filtered_products = candidate_products
        
        filtered_products = filtered_products.annotate(
            favorite_count=Count('favorite', distinct=True)
        )[:50]
        
        for product in filtered_products:
            # 计算卖家信用权重
            seller_credit = calculate_user_credit_score(product.seller)
            
            # 基础分数
            base_score = product.views * 0.6 + product.favorite_count * 5
            
            # 计算商品相似度分数（基于用户最近浏览和收藏）
            similarity_score = 0
            reference_products = recent_browsed_products + favorite_products
            
            if reference_products:
                for ref_product in reference_products[:3]:
                    sim = calculate_product_similarity(product, ref_product)
                    similarity_score += sim
                similarity_score = similarity_score / min(len(reference_products), 3)
            
            # 应用信用权重（卖家信用影响推荐分数）
            final_score = (base_score * 0.5 + similarity_score * 0.3) * seller_credit
            
            # 应用校园周期性因子
            if product.category.name in seasonal_categories:
                final_score *= campus_period_factor
            
            # 生成推荐理由
            reason = []
            if product.category.name in preferred_category_names:
                reason.append(f"你常浏览{product.category.name}")
            if product.category.name in seasonal_categories:
                reason.append("当季热门")
            if similarity_score > 60:
                reason.append("与你浏览过的相似")
            if product.views > 100:
                reason.append("近期高热度")
            if seller_credit >= 0.8:
                reason.append("高信用卖家")
            
            recommended_products_with_scores.append({
                'product': product,
                'score': final_score,
                'reason': '、'.join(reason) if reason else '热门推荐',
                'seller_credit': seller_credit
            })
    else:
        # 未登录用户：基于热门趋势 + 校园周期性推荐
        hot_products = Product.objects.filter(
            status='available'
        ).exclude(id__in=hot_product_ids)
        
        # 先尝试从季节性分类选择
        seasonal_products = hot_products.filter(category__name__in=seasonal_categories)
        
        # 如果季节性商品不足，补充其他商品
        if seasonal_products.count() < 4:
            other_products = hot_products.exclude(category__name__in=seasonal_categories)
            hot_products = list(seasonal_products.annotate(favorite_count=Count('favorite', distinct=True)).order_by('-views', '-favorite_count')[:20])
            hot_products += list(other_products.annotate(favorite_count=Count('favorite', distinct=True)).order_by('-views', '-favorite_count')[:30])
        else:
            hot_products = seasonal_products.annotate(favorite_count=Count('favorite', distinct=True)).order_by('-views', '-favorite_count')[:30]
        
        for product in hot_products:
            seller_credit = calculate_user_credit_score(product.seller)
            base_score = product.views * 0.6 + product.favorite_count * 5
            final_score = base_score * seller_credit
            
            # 应用校园周期性因子
            if product.category.name in seasonal_categories:
                final_score *= campus_period_factor
            
            reason = []
            if product.category.name in seasonal_categories:
                reason.append("当季热门")
            if product.views > 100:
                reason.append("近期高热度")
            if seller_credit >= 0.8:
                reason.append("高信用卖家")
            
            recommended_products_with_scores.append({
                'product': product,
                'score': final_score,
                'reason': '、'.join(reason) if reason else '热门推荐',
                'seller_credit': seller_credit
            })
    
    # 按分数排序，取前4个
    recommended_products_with_scores.sort(key=lambda x: x['score'], reverse=True)
    top_recommendations = recommended_products_with_scores[:4]
    
    # 格式化推荐项
    recommendations = []
    for item in top_recommendations:
        product = item['product']
        favorite_count = product.favorite_set.count() if hasattr(product, 'favorite_set') else 0
        
        recommendations.append({
            'id': product.id,
            'title': product.title,
            'price': product.price,
            'image': product.image.url if product.image else None,
            'category': product.category.name,
            'views': product.views,
            'favorite_count': favorite_count,
            'url': f'/products/{product.id}/',
            'reason': item['reason'],
            'seller_credit': round(item['seller_credit'] * 100)
        })
    
    return {
        'user_recommendations': recommendations,
    }
