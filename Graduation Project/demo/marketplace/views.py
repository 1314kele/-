from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from .models import Category, Product, Favorite, Message, Review, Transaction, UserBehavior, AbnormalBehavior, BehaviorConfig, Warning, BehaviorReport, SystemLog, Notification, Wallet, WalletTransaction, Payment, SecurityLog
from .forms import ProductForm, MessageForm, ReviewForm, SearchForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime, timedelta
import json
from django.http import JsonResponse
from django.db import models as django_models
from django.utils import timezone
from .security import SecurityValidator, log_security_event, send_security_alert

User = get_user_model()

def log_user_behavior(request, action_type, action_data=None):
    """
    记录用户行为到知识库
    """
    if not request.user.is_authenticated:
        return
    
    try:
        ip_address = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referer = request.META.get('HTTP_REFERER', '')
        session_id = request.session.session_key or ''
        
        UserBehavior.objects.create(
            user=request.user,
            action_type=action_type,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
            action_data=json.dumps(action_data, ensure_ascii=False) if action_data else None,
            session_id=session_id
        )
    except Exception:
        pass

# 检查用户是否为管理员
def is_admin(user):
    return user.is_staff

# 首页
def home(request):
    """首页视图"""
    latest_products = Product.objects.all().order_by('-created_at')[:10]  # 显示最近10个商品
    popular_products = Product.objects.all().order_by('-views')[:10]  # 显示最热门10个商品（按浏览量排序）
    categories = Category.objects.all()
    
    # 统计数据
    from django.contrib.auth import get_user_model
    User = get_user_model()
    total_products = Product.objects.count()
    total_users = User.objects.count()
    completed_transactions = Transaction.objects.filter(status='completed').count()
    
    return render(request, 'marketplace/home.html', {
        'latest_products': latest_products, 
        'popular_products': popular_products, 
        'categories': categories,
        'total_products': total_products,
        'total_users': total_users,
        'completed_transactions': completed_transactions
    })

# 商品列表
def product_list(request):
    """商品列表视图"""
    products = Product.objects.all()
    categories = Category.objects.all()
    
    # 获取筛选参数
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', 'all')
    category_id = request.GET.get('category', '')
    sort_by = request.GET.get('sort', '-created_at')
    
    # 搜索筛选
    if query:
        products = products.filter(title__icontains=query)
    
    # 状态筛选
    if status_filter != 'all':
        products = products.filter(status=status_filter)
    
    # 分类筛选
    if category_id:
        products = products.filter(category_id=category_id)
    
    # 排序
    products = products.order_by(sort_by)
    
    # 分页
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(products, 8)  # 每页显示8个商品
    page = request.GET.get('page', 1)
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    # 获取选中的分类对象
    selected_category = None
    if category_id:
        try:
            selected_category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            pass
    
    return render(request, 'marketplace/product_list.html', {
        'products': products,
        'categories': categories,
        'query': query,
        'status_filter': status_filter,
        'selected_category': selected_category,
        'sort_by': sort_by
    })

# 商品详情
def product_detail(request, product_id):
    """商品详情视图"""
    product = get_object_or_404(Product, id=product_id)
    # 增加商品浏览次数
    product.views += 1
    product.save()
    
    # 记录浏览行为到知识库
    log_user_behavior(request, 'browse', {
        'product_id': product.id,
        'product_title': product.title,
        'category_id': product.category.id,
        'category_name': product.category.name,
        'price': float(product.price)
    })
    
    return render(request, 'marketplace/product_detail.html', {'product': product})

# 添加商品
@login_required
def add_product(request):
    """添加商品视图"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, '商品发布成功！')
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductForm()
    return render(request, 'marketplace/add_product.html', {'form': form})

# 编辑商品
@login_required
def edit_product(request, product_id):
    """编辑商品视图"""
    product = get_object_or_404(Product, id=product_id)
    # 只有商品发布者可以编辑商品
    if product.seller != request.user:
        messages.error(request, '您没有权限编辑此商品！')
        return redirect('product_detail', product_id=product.id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, '商品更新成功！')
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'marketplace/edit_product.html', {'form': form, 'product': product})

# 分类列表
def category_list(request):
    """分类列表视图"""
    categories = Category.objects.all()
    return render(request, 'marketplace/category_list.html', {'categories': categories})

# 分类商品
def category_products(request, category_id):
    """分类商品视图"""
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category).order_by('-created_at')
    return render(request, 'marketplace/category_products.html', {'category': category, 'products': products})

# 收藏商品
@login_required
def toggle_favorite(request, product_id):
    """切换商品收藏状态视图"""
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    
    # 记录收藏或取消收藏行为到知识库
    action_type = 'favorite' if created else 'unfavorite'
    log_user_behavior(request, action_type, {
        'product_id': product.id,
        'product_title': product.title,
        'category_id': product.category.id,
        'category_name': product.category.name
    })
    
    if not created:
        favorite.delete()
    return redirect('product_detail', product_id=product_id)

# 收藏列表
def favorite_list(request):
    """收藏列表视图"""
    favorites = Favorite.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'marketplace/favorite_list.html', {'favorites': favorites})

# 发送消息
@login_required
def send_message(request, product_id):
    """发送消息视图"""
    product = get_object_or_404(Product, id=product_id)
    
    # 支持通过URL参数传入特定的接收者（用于卖家回复买家）
    receiver_id = request.GET.get('receiver_id')
    if receiver_id:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        receiver = get_object_or_404(User, id=receiver_id)
    else:
        receiver = product.seller

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.product = product
            message.save()
            messages.success(request, '消息发送成功！')
            # 如果是从消息列表过来的回复，发完跳回消息列表
            if receiver_id:
                return redirect('message_list')
            return redirect('product_detail', product_id=product.id)
    else:
        form = MessageForm()
    return render(request, 'marketplace/send_message.html', {'form': form, 'product': product, 'receiver': receiver})

# 消息列表
@login_required
def message_list(request):
    """消息列表视图"""
    received_messages = Message.objects.filter(receiver=request.user).order_by('-created_at')
    sent_messages = Message.objects.filter(sender=request.user).order_by('-created_at')
    # 标记收到的消息为已读
    received_messages.filter(is_read=False).update(is_read=True)
    return render(request, 'marketplace/message_list.html', {
        'received_messages': received_messages,
        'sent_messages': sent_messages
    })

# 添加评价
@login_required
def add_review(request, product_id):
    """添加评价视图"""
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.reviewed_user = product.seller
            review.product = product
            review.save()
            messages.success(request, '评价成功！')
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()
    return render(request, 'marketplace/add_review.html', {'form': form, 'product': product})

# 自定义登录视图 - 增加异常登录检测
def login(request):
    """自定义登录视图，包含安全检测"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # 尝试认证用户
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # 记录登录事件
            log_security_event(
                user=user,
                log_type='login',
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details='用户登录'
            )
            
            # 检测异常登录行为
            is_abnormal = SecurityValidator.detect_abnormal_login(user, request)
            
            if is_abnormal:
                # 发送安全预警邮件
                send_security_alert(
                    user=user,
                    alert_type='异常登录检测',
                    alert_message='系统检测到您的账户存在异常登录行为。'
                )
                messages.warning(request, '检测到异常登录，请注意账户安全！')
            
            # 执行登录
            auth_login(request, user)
            
            # 记录用户行为
            log_user_behavior(request, 'login')
            
            # 获取next参数或重定向到首页
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, '用户名或密码错误！')
    
    return render(request, 'registration/login.html')

# 注册
def register(request):
    """用户注册视图 - 增加邮箱验证和密码强度检查"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email', '')
            
            # 验证邮箱域名（校园邮箱验证）
            if email and not SecurityValidator.validate_email_domain(email):
                messages.error(request, '仅允许使用校园邮箱注册！')
                return render(request, 'marketplace/register.html', {'form': form})
            
            # 验证密码强度
            password = form.cleaned_data.get('password1', '')
            is_valid, password_msg = SecurityValidator.validate_password_strength(password)
            if not is_valid:
                messages.error(request, password_msg)
                return render(request, 'marketplace/register.html', {'form': form})
            
            user = form.save()
            
            # 记录注册事件
            log_security_event(
                user=user,
                log_type='suspicious',
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details='新用户注册'
            )
            
            messages.success(request, f'注册成功！欢迎 {user.username}')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'marketplace/register.html', {'form': form})

# 创建交易
def create_transaction(request, product_id):
    """创建交易视图"""
    product = get_object_or_404(Product, id=product_id)
    if product.status != 'available':
        messages.error(request, '此商品已不可交易！')
        return redirect('product_detail', product_id=product_id)
    
    # 检查买家是否为商品发布者
    if request.user == product.seller:
        messages.error(request, '您不能购买自己发布的商品！')
        return redirect('product_detail', product_id=product_id)
    
    # 创建交易记录
    transaction = Transaction.objects.create(
        buyer=request.user,
        seller=product.seller,
        product=product,
        price=product.price
    )
    
    # 发送通知给卖家
    Notification.objects.create(
        user=product.seller,
        notification_type='transaction',
        title='新的交易请求',
        content=f'用户 {request.user.username} 想要购买您的商品 "{product.title}"',
        link=f'/transactions/{transaction.id}/'
    )
    
    # 发送通知给买家
    Notification.objects.create(
        user=request.user,
        notification_type='transaction',
        title='交易请求已创建',
        content=f'您已成功创建对商品 "{product.title}" 的交易请求，等待卖家确认',
        link=f'/transactions/{transaction.id}/'
    )
    
    messages.success(request, '交易创建成功！等待卖家确认')
    return redirect('transaction_detail', transaction_id=transaction.id)

# 交易详情
def transaction_detail(request, transaction_id):
    """交易详情视图"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    # 只有交易相关人员可以查看交易详情
    if request.user not in [transaction.buyer, transaction.seller]:
        messages.error(request, '您没有权限查看此交易详情！')
        return redirect('home')
    return render(request, 'marketplace/transaction_detail.html', {'transaction': transaction})

# 确认交易
@login_required
def confirm_transaction(request, transaction_id):
    """确认交易视图"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    # 只有卖家可以确认交易
    if request.user != transaction.seller:
        messages.error(request, '您没有权限确认此交易！')
        return redirect('transaction_detail', transaction_id=transaction.id)
    
    transaction.confirm_transaction()
    
    # 发送通知给买家
    Notification.objects.create(
        user=transaction.buyer,
        notification_type='transaction',
        title='交易已确认',
        content=f'卖家已确认您对商品 "{transaction.product.title}" 的交易请求',
        link=f'/transactions/{transaction.id}/'
    )
    
    messages.success(request, '交易已确认！')
    return redirect('transaction_detail', transaction_id=transaction.id)

# 完成交易
@login_required
def complete_transaction(request, transaction_id):
    """完成交易视图"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    # 只有买家可以确认交易完成
    if request.user != transaction.buyer:
        messages.error(request, '您没有权限完成此交易！')
        return redirect('transaction_detail', transaction_id=transaction.id)
    
    transaction.complete_transaction()
    
    # 发送通知给卖家
    Notification.objects.create(
        user=transaction.seller,
        notification_type='transaction',
        title='交易已完成',
        content=f'买家已确认收到商品 "{transaction.product.title}"，交易已完成',
        link=f'/transactions/{transaction.id}/'
    )
    
    messages.success(request, '交易已完成！')
    return redirect('transaction_detail', transaction_id=transaction.id)

# 取消交易
@login_required
def cancel_transaction(request, transaction_id):
    """取消交易视图"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    # 只有交易相关人员可以取消交易
    if request.user not in [transaction.buyer, transaction.seller]:
        messages.error(request, '您没有权限取消此交易！')
        return redirect('transaction_detail', transaction_id=transaction.id)
    
    transaction.status = 'cancelled'
    transaction.save()
    
    # 发送通知给对方
    recipient = transaction.seller if request.user == transaction.buyer else transaction.buyer
    action_by = '买家' if request.user == transaction.buyer else '卖家'
    
    Notification.objects.create(
        user=recipient,
        notification_type='transaction',
        title='交易已取消',
        content=f'{action_by}已取消对商品 "{transaction.product.title}" 的交易',
        link=f'/transactions/{transaction.id}/'
    )
    
    messages.success(request, '交易已取消！')
    return redirect('transaction_detail', transaction_id=transaction.id)

# 订单管理
@login_required
def order_management(request):
    """订单管理页面"""
    # 获取用户作为买家和卖家的所有交易
    buyer_transactions = Transaction.objects.filter(buyer=request.user)
    seller_transactions = Transaction.objects.filter(seller=request.user)
    
    # 计算订单统计数据
    total_orders = buyer_transactions.count() + seller_transactions.count()
    pending_orders = buyer_transactions.filter(status='pending').count() + seller_transactions.filter(status='pending').count()
    confirmed_orders = buyer_transactions.filter(status='confirmed').count() + seller_transactions.filter(status='confirmed').count()
    completed_orders = buyer_transactions.filter(status='completed').count() + seller_transactions.filter(status='completed').count()
    
    context = {
        'stats': {
            'total': total_orders,
            'pending': pending_orders,
            'confirmed': confirmed_orders,
            'completed': completed_orders
        }
    }
    
    return render(request, 'marketplace/order_management.html', context)

# AJAX获取订单列表
@login_required
def order_list_ajax(request):
    """AJAX获取订单列表"""
    # 获取用户作为买家和卖家的所有交易
    buyer_transactions = Transaction.objects.filter(buyer=request.user)
    seller_transactions = Transaction.objects.filter(seller=request.user)
    
    # 计算订单统计数据
    total_orders = buyer_transactions.count() + seller_transactions.count()
    pending_orders = buyer_transactions.filter(status='pending').count() + seller_transactions.filter(status='pending').count()
    confirmed_orders = buyer_transactions.filter(status='confirmed').count() + seller_transactions.filter(status='confirmed').count()
    completed_orders = buyer_transactions.filter(status='completed').count() + seller_transactions.filter(status='completed').count()
    
    # 获取筛选参数
    order_id = request.GET.get('order_id', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    status_filter = request.GET.get('status', '')
    role_filter = request.GET.get('role', '')
    keyword = request.GET.get('keyword', '')
    
    # 合并交易记录
    all_transactions = list(buyer_transactions) + list(seller_transactions)
    
    # 应用筛选条件
    filtered_transactions = []
    for transaction in all_transactions:
        # 订单ID筛选
        if order_id and str(transaction.id) != order_id:
            continue
            
        # 日期筛选
        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            if transaction.created_at.date() < start_date_obj:
                continue
                
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            if transaction.created_at.date() > end_date_obj:
                continue
                
        # 状态筛选
        if status_filter and transaction.status != status_filter:
            continue
            
        # 角色筛选
        if role_filter:
            if role_filter == 'buyer' and transaction.buyer != request.user:
                continue
            if role_filter == 'seller' and transaction.seller != request.user:
                continue
                
        # 关键词搜索
        if keyword:
            keyword_lower = keyword.lower()
            product_title_lower = transaction.product.title.lower()
            product_desc_lower = transaction.product.description.lower()
            other_user = transaction.seller.username if transaction.buyer == request.user else transaction.buyer.username
            other_user_lower = other_user.lower()
            
            if (keyword_lower not in product_title_lower and 
                keyword_lower not in product_desc_lower and 
                keyword_lower not in other_user_lower):
                continue
                
        filtered_transactions.append(transaction)
    
    # 按创建时间排序
    filtered_transactions.sort(key=lambda x: x.created_at, reverse=True)
    
    # 分页处理
    page_size = int(request.GET.get('page_size', 20))
    page = int(request.GET.get('page', 1))
    
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_transactions = filtered_transactions[start_index:end_index]
    
    # 构建返回数据
    transactions_data = []
    for transaction in paginated_transactions:
        is_buyer = transaction.buyer == request.user
        other_user = transaction.seller if is_buyer else transaction.buyer
        
        transactions_data.append({
            'id': transaction.id,
            'product_id': transaction.product.id,
            'product_title': transaction.product.title,
            'product_description': transaction.product.description,
            'product_image': transaction.product.image.url if transaction.product.image else None,
            'price': float(transaction.price),
            'buyer': transaction.buyer.username,
            'seller': transaction.seller.username,
            'status': transaction.status,
            'status_text': transaction.get_status_display(),
            'role': 'buyer' if is_buyer else 'seller',
            'other_user': other_user.username,
            'created_at': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'confirmed_at': transaction.confirmed_at.strftime('%Y-%m-%d %H:%M:%S') if transaction.confirmed_at else None,
            'completed_at': transaction.completed_at.strftime('%Y-%m-%d %H:%M:%S') if transaction.completed_at else None,
            'is_buyer': is_buyer
        })
    
    # 分页信息
    total_pages = (len(filtered_transactions) + page_size - 1) // page_size
    
    return JsonResponse({
        'success': True,
        'stats': {
            'total': total_orders,
            'pending': pending_orders,
            'confirmed': confirmed_orders,
            'completed': completed_orders
        },
        'orders': transactions_data,
        'pagination': {
            'current_page': page,
            'total_pages': total_pages,
            'total_items': len(filtered_transactions),
            'has_previous': page > 1,
            'has_next': page < total_pages,
            'page_size': page_size
        }
    })

# AJAX获取订单详情
@login_required
def order_detail_ajax(request, transaction_id):
    """AJAX获取订单详情"""
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        # 检查权限
        if request.user not in [transaction.buyer, transaction.seller]:
            return JsonResponse({'error': '无权限查看此订单'}, status=403)
        
        # 构建返回数据
        transaction_data = {
            'id': transaction.id,
            'product_name': transaction.product.title,
            'product_description': transaction.product.description,
            'price': float(transaction.price),
            'buyer': transaction.buyer.username,
            'seller': transaction.seller.username,
            'status': transaction.status,
            'created_at': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'complete_time': transaction.complete_time.strftime('%Y-%m-%d %H:%M:%S') if transaction.complete_time else None,
            'is_buyer': transaction.buyer == request.user
        }
        
        return JsonResponse(transaction_data)
    except Transaction.DoesNotExist:
        return JsonResponse({'error': '订单不存在'}, status=404)

# 用户行为分析仪表盘
@login_required
@user_passes_test(is_admin)
def behavior_analysis_dashboard(request):
    """
    用户行为分析仪表盘
    展示平台整体及各维度的用户行为分析结果
    """
    return render(request, 'marketplace/behavior_analysis_dashboard.html')

# 获取行为统计数据
@login_required
@user_passes_test(is_admin)
def get_behavior_stats(request):
    """
    获取行为统计数据（用于图表）
    """
    # 获取最近7天的日期列表
    dates = []
    behavior_counts = []
    abnormal_counts = []
    risk_scores = []
    
    for i in range(7):
        date = datetime.now() - timedelta(days=6-i)
        date_str = date.strftime('%Y-%m-%d')
        dates.append(date_str)
        
        # 获取当天的行为数量
        start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        behavior_count = UserBehavior.objects.filter(
            action_time__gte=start_time,
            action_time__lte=end_time
        ).count()
        behavior_counts.append(behavior_count)
        
        # 获取当天的异常行为数量
        abnormal_count = AbnormalBehavior.objects.filter(
            detected_time__gte=start_time,
            detected_time__lte=end_time
        ).count()
        abnormal_counts.append(abnormal_count)
        
        # 获取当天的平均风险分数
        abnormal_behaviors = AbnormalBehavior.objects.filter(
            detected_time__gte=start_time,
            detected_time__lte=end_time
        )
        if abnormal_behaviors.exists():
            avg_risk_score = sum(ab.risk_score for ab in abnormal_behaviors) / len(abnormal_behaviors)
            risk_scores.append(round(avg_risk_score, 2))
        else:
            risk_scores.append(0)
    
    # 获取异常行为类型分布
    abnormal_types = {
        'login': '异常登录',
        'frequency': '异常操作频率',
        'transaction': '异常交易金额',
        'automation': '脚本自动化操作',
        'other': '其他异常'
    }
    type_counts = {}
    for type_key, type_name in abnormal_types.items():
        type_counts[type_name] = AbnormalBehavior.objects.filter(
            abnormal_type=type_key,
            detected_time__gte=datetime.now() - timedelta(days=7)
        ).count()
    
    # 获取风险用户分布
    risk_levels = {
        'low': {'label': '低风险 (0-50分)', 'count': 0},
        'medium': {'label': '中风险 (50-100分)', 'count': 0},
        'high': {'label': '高风险 (100分以上)', 'count': 0}
    }
    
    # 这里简化实现，实际应计算每个用户的风险分数
    # 由于计算用户风险分数可能比较耗时，这里仅作示例
    high_risk_users = BehaviorReport.objects.filter(
        total_score__gte=100,
        report_time__gte=datetime.now() - timedelta(days=7)
    ).count()
    
    medium_risk_reports = BehaviorReport.objects.filter(
        total_score__gte=50,
        total_score__lt=100,
        report_time__gte=datetime.now() - timedelta(days=7)
    ).count()
    
    # 这里简化计算，实际应从用户表中获取所有用户并计算风险分数
    # 由于缺少实际数据，这里仅作示例
    risk_levels['high']['count'] = high_risk_users
    risk_levels['medium']['count'] = medium_risk_reports
    risk_levels['low']['count'] = 100  # 假设低风险用户数量为100
    
    # 准备返回数据
    data = {
        'dates': dates,
        'behavior_counts': behavior_counts,
        'abnormal_counts': abnormal_counts,
        'risk_scores': risk_scores,
        'type_counts': type_counts,
        'risk_levels': risk_levels
    }
    
    return JsonResponse(data)

def wallet_view(request):
    """钱包页面"""
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')[:20]
    
    return render(request, 'marketplace/wallet.html', {
        'wallet': wallet,
        'transactions': transactions
    })

@login_required
def recharge_wallet(request):
    """钱包充值"""
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        
        try:
            from decimal import Decimal
            amount = Decimal(str(amount))
            if amount <= 0:
                messages.error(request, '充值金额必须大于0')
                return redirect('wallet_view')
            
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            
            wallet_transaction = WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='recharge',
                amount=amount,
                balance_before=wallet.balance,
                balance_after=wallet.balance + amount,
                status='pending',
                description=f'{payment_method}充值'
            )
            
            messages.success(request, '充值申请已提交，等待处理')
            return redirect('wallet_view')
            
        except Exception as e:
            messages.error(request, f'充值失败：{str(e)}')
            return redirect('wallet_view')
    
    return render(request, 'marketplace/recharge.html')

@login_required
def withdraw_wallet(request):
    """钱包提现"""
    if request.method == 'POST':
        amount = request.POST.get('amount')
        
        try:
            from decimal import Decimal
            amount = Decimal(str(amount))
            if amount <= 0:
                messages.error(request, '提现金额必须大于0')
                return redirect('wallet_view')
            
            wallet = Wallet.objects.get(user=request.user)
            
            if wallet.balance < amount:
                messages.error(request, '余额不足')
                return redirect('wallet_view')
            
            wallet_transaction = WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='withdraw',
                amount=amount,
                balance_before=wallet.balance,
                balance_after=wallet.balance - amount,
                status='pending',
                description='提现申请'
            )
            
            wallet.balance -= amount
            wallet.save()
            
            messages.success(request, '提现申请已提交，等待处理')
            return redirect('wallet_view')
            
        except Exception as e:
            messages.error(request, f'提现失败：{str(e)}')
            return redirect('wallet_view')
    
    return render(request, 'marketplace/withdraw.html')

@login_required
def process_payment(request, transaction_id):
    """处理支付"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    if transaction.buyer != request.user:
        messages.error(request, '您没有权限支付此交易')
        return redirect('transaction_detail', transaction_id=transaction.id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'wallet':
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            
            if wallet.balance < transaction.price:
                messages.error(request, '钱包余额不足')
                return redirect('transaction_detail', transaction_id=transaction.id)
            
            wallet.balance -= transaction.price
            wallet.save()
            
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='payment',
                amount=transaction.price,
                balance_before=wallet.balance + transaction.price,
                balance_after=wallet.balance,
                status='completed',
                description=f'支付商品: {transaction.product.title}',
                related_transaction=transaction
            )
            
            Payment.objects.create(
                transaction=transaction,
                payment_method='wallet',
                amount=transaction.price,
                status='completed',
                payment_time=timezone.now()
            )
            
            messages.success(request, '支付成功！')
            return redirect('transaction_detail', transaction_id=transaction.id)
        
        else:
            Payment.objects.create(
                transaction=transaction,
                payment_method=payment_method,
                amount=transaction.price,
                status='pending'
            )
            
            messages.success(request, '支付请求已提交，请完成支付')
            return redirect('transaction_detail', transaction_id=transaction.id)
    
    return render(request, 'marketplace/payment.html', {'transaction': transaction})

def map_view(request):
    """地图视图"""
    products = Product.objects.filter(
        status='available',
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('category', 'seller')[:50]
    
    return render(request, 'marketplace/map.html', {'products': products})

def calculate_distance(request):
    """计算距离API"""
    lat1 = request.GET.get('lat1')
    lon1 = request.GET.get('lon1')
    lat2 = request.GET.get('lat2')
    lon2 = request.GET.get('lon2')
    
    if not all([lat1, lon1, lat2, lon2]):
        return JsonResponse({'error': '缺少必要参数'}, status=400)
    
    try:
        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)
        
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        
        return JsonResponse({
            'distance': round(distance, 2),
            'unit': 'km'
        })
    except ValueError:
        return JsonResponse({'error': '无效的坐标'}, status=400)

def haversine_distance(lat1, lon1, lat2, lon2):
    """使用Haversine公式计算两点间距离"""
    from math import radians, cos, sin, asin, sqrt
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    r = 6371
    return c * r

def nearby_products(request):
    """附近商品API"""
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    radius = request.GET.get('radius', 5)
    
    if not all([lat, lon]):
        return JsonResponse({'error': '缺少必要参数'}, status=400)
    
    try:
        lat = float(lat)
        lon = float(lon)
        radius = float(radius)
        
        products = Product.objects.filter(
            status='available',
            latitude__isnull=False,
            longitude__isnull=False
        ).select_related('category', 'seller')
        
        nearby_products = []
        for product in products:
            distance = haversine_distance(lat, lon, product.latitude, product.longitude)
            if distance <= radius:
                nearby_products.append({
                    'id': product.id,
                    'title': product.title,
                    'price': str(product.price),
                    'latitude': product.latitude,
                    'longitude': product.longitude,
                    'distance': round(distance, 2),
                    'category': product.category.name,
                    'seller': product.seller.username,
                    'image': product.image.url if product.image else None
                })
        
        nearby_products.sort(key=lambda x: x['distance'])
        
        return JsonResponse({
            'products': nearby_products[:20],
            'total': len(nearby_products)
        })
    except ValueError:
        return JsonResponse({'error': '无效的坐标'}, status=400)

def search_products(request):
    """商品搜索视图"""
    form = SearchForm(request.GET or None)
    products = Product.objects.filter(status='available')
    search_query = None
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        condition = form.cleaned_data.get('condition')
        sort_by = form.cleaned_data.get('sort_by')
        
        if query:
            search_query = query
            products = products.filter(
                title__icontains=query
            ) | products.filter(
                description__icontains=query
            )
        
        if category:
            products = products.filter(category=category)
        
        if min_price:
            products = products.filter(price__gte=min_price)
        
        if max_price:
            products = products.filter(price__lte=max_price)
        
        if condition:
            products = products.filter(condition=condition)
        
        if sort_by:
            if sort_by == 'price_asc':
                products = products.order_by('price')
            elif sort_by == 'price_desc':
                products = products.order_by('-price')
            elif sort_by == 'views':
                products = products.order_by('-views')
            elif sort_by == 'created_at':
                products = products.order_by('-created_at')
    
    categories = Category.objects.all()
    
    # 记录搜索行为到知识库
    if search_query:
        log_user_behavior(request, 'search', {
            'query': search_query,
            'result_count': products.count(),
            'category': category.id if category else None,
            'category_name': category.name if category else None
        })
    
    return render(request, 'marketplace/search.html', {
        'form': form,
        'products': products,
        'categories': categories
    })

def search_suggestions(request):
    """搜索建议API"""
    query = request.GET.get('q', '')
    suggestions = []
    
    if query:
        products = Product.objects.filter(
            title__icontains=query,
            status='available'
        )[:10]
        
        for product in products:
            suggestions.append({
                'id': product.id,
                'title': product.title,
                'price': str(product.price),
                'image': product.image.url if product.image else None
            })
    
    return JsonResponse({'suggestions': suggestions})

def notification_list(request):
    """通知列表"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'marketplace/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def mark_notification_read(request, notification_id):
    """标记通知为已读"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if notification.link:
        return redirect(notification.link)
    return redirect('notification_list')

@login_required
def mark_all_notifications_read(request):
    """标记所有通知为已读"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, '所有通知已标记为已读')
    return redirect('notification_list')

@login_required
def get_unread_notifications(request):
    """获取未读通知数量"""
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread_count})

@login_required
def get_latest_notifications(request):
    """获取最新通知"""
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    notification_list = []
    for notification in notifications:
        notification_list.append({
            'id': notification.id,
            'type': notification.notification_type,
            'title': notification.title,
            'content': notification.content,
            'link': notification.link,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({'notifications': notification_list})

def statistics_dashboard(request):
    """数据统计仪表板"""
    if not request.user.is_staff:
        messages.error(request, '您没有权限访问此页面')
        return redirect('home')
    
    return render(request, 'marketplace/statistics.html')

def get_statistics_data(request):
    """获取统计数据API"""
    if not request.user.is_staff:
        return JsonResponse({'error': '无权限'}, status=403)
    
    # 商品统计
    total_products = Product.objects.count()
    available_products = Product.objects.filter(status='available').count()
    sold_products = Product.objects.filter(status='sold').count()
    
    # 用户统计
    total_users = User.objects.count()
    active_users = User.objects.filter(
        id__in=UserBehavior.objects.filter(
            action_time__gte=timezone.now() - timedelta(days=7)
        ).values_list('user_id', flat=True)
    ).count()
    
    # 交易统计
    total_transactions = Transaction.objects.count()
    completed_transactions = Transaction.objects.filter(status='completed').count()
    total_amount = Transaction.objects.filter(status='completed').aggregate(
        total=django_models.Sum('price')
    )['total'] or 0
    
    # 分类统计
    category_stats = []
    for category in Category.objects.all():
        product_count = Product.objects.filter(category=category).count()
        if product_count > 0:
            category_stats.append({
                'name': category.name,
                'count': product_count
            })
    
    # 最近7天交易趋势
    dates = []
    transaction_counts = []
    for i in range(7):
        date = timezone.now() - timedelta(days=6-i)
        date_str = date.strftime('%Y-%m-%d')
        dates.append(date_str)
        
        count = Transaction.objects.filter(
            created_at__date=date.date()
        ).count()
        transaction_counts.append(count)
    
    # 商品状况分布
    condition_stats = {}
    for condition, label in Product.CONDITION_CHOICES:
        count = Product.objects.filter(condition=condition).count()
        if count > 0:
            condition_stats[label] = count
    
    data = {
        'products': {
            'total': total_products,
            'available': available_products,
            'sold': sold_products
        },
        'users': {
            'total': total_users,
            'active': active_users
        },
        'transactions': {
            'total': total_transactions,
            'completed': completed_transactions,
            'total_amount': float(total_amount)
        },
        'categories': category_stats,
        'trend': {
            'dates': dates,
            'counts': transaction_counts
        },
        'conditions': condition_stats
    }
    
    return JsonResponse(data)

@login_required
def check_new_messages(request):
    count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return JsonResponse({'has_new': count > 0, 'count': count})
