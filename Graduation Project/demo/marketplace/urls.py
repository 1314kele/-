from django.urls import path
from . import views

urlpatterns = [
    # 首页和商品相关
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    
    # 分类功能
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:category_id>/', views.category_products, name='category_products'),
    
    # 收藏功能
    path('products/<int:product_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorite_list, name='favorite_list'),
    
    # 消息功能
    path('products/<int:product_id>/message/', views.send_message, name='send_message'),
    path('messages/', views.message_list, name='message_list'),
    path('api/messages/check/', views.check_new_messages, name='check_new_messages'),
    
    # 评价功能
    path('products/<int:product_id>/review/', views.add_review, name='add_review'),
    
    # 用户认证
    path('register/', views.register, name='register'),
    
    # 交易功能
    path('transactions/create/<int:product_id>/', views.create_transaction, name='create_transaction'),
    path('transactions/<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('transactions/<int:transaction_id>/confirm/', views.confirm_transaction, name='confirm_transaction'),
    path('transactions/<int:transaction_id>/complete/', views.complete_transaction, name='complete_transaction'),
    path('transactions/<int:transaction_id>/cancel/', views.cancel_transaction, name='cancel_transaction'),

    
    # 订单管理功能
    path('orders/', views.order_management, name='order_management'),
    path('orders/ajax/', views.order_list_ajax, name='order_list_ajax'),
    path('orders/<int:transaction_id>/detail/', views.order_detail_ajax, name='order_detail_ajax'),
    
    # 用户行为分析功能
    path('behavior_analysis/dashboard/', views.behavior_analysis_dashboard, name='behavior_analysis_dashboard'),
    path('behavior_analysis/get_stats/', views.get_behavior_stats, name='get_behavior_stats'),
    
    # 搜索功能
    path('search/', views.search_products, name='search_products'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    
    # 通知功能
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/unread-count/', views.get_unread_notifications, name='get_unread_notifications'),
    path('notifications/latest/', views.get_latest_notifications, name='get_latest_notifications'),
    
    # 数据统计功能
    path('statistics/', views.statistics_dashboard, name='statistics_dashboard'),
    path('statistics/data/', views.get_statistics_data, name='get_statistics_data'),
    
    # 支付功能
    path('wallet/', views.wallet_view, name='wallet_view'),
    path('wallet/recharge/', views.recharge_wallet, name='recharge_wallet'),
    path('wallet/withdraw/', views.withdraw_wallet, name='withdraw_wallet'),
    path('transactions/<int:transaction_id>/pay/', views.process_payment, name='process_payment'),
    
    # 地图功能
    path('map/', views.map_view, name='map_view'),
    path('api/calculate-distance/', views.calculate_distance, name='calculate_distance'),
    path('api/nearby-products/', views.nearby_products, name='nearby_products'),
]