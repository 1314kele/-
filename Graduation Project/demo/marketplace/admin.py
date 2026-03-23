from django.contrib import admin
from django.utils import timezone
from .models import Category, Product, Favorite, Message, Review, Transaction, UserBehavior, AbnormalBehavior, BehaviorConfig, Warning, BehaviorReport, SystemLog

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'price', 'category', 'condition', 'status', 'created_at']
    list_filter = ['category', 'condition', 'status', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['views', 'created_at', 'updated_at']
    fieldsets = [
        ('基本信息', {
            'fields': ['title', 'description', 'price', 'category', 'seller']
        }),
        ('商品详情', {
            'fields': ['condition', 'status', 'location', 'contact_info', 'image']
        }),
        ('统计信息', {
            'fields': ['views', 'created_at', 'updated_at']
        }),
    ]

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__title']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'product', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'receiver__username', 'product__title']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'reviewed_user', 'product', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['reviewer__username', 'reviewed_user__username', 'product__title']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'seller', 'product', 'price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['buyer__username', 'seller__username', 'product__title']
    readonly_fields = ['created_at', 'confirmed_at', 'completed_at']
    fieldsets = [
        ('交易信息', {
            'fields': ['buyer', 'seller', 'product', 'price', 'status']
        }),
        ('时间信息', {
            'fields': ['created_at', 'confirmed_at', 'completed_at']
        }),
    ]


@admin.register(UserBehavior)
class UserBehaviorAdmin(admin.ModelAdmin):
    """用户行为数据管理员"""
    list_display = ['user', 'action_type', 'action_time', 'ip_address', 'session_id']
    list_filter = ['action_type', 'action_time']
    search_fields = ['user__username', 'ip_address', 'session_id']
    readonly_fields = ['action_time']
    date_hierarchy = 'action_time'
    fieldsets = [
        ('用户信息', {
            'fields': ['user', 'session_id']
        }),
        ('行为信息', {
            'fields': ['action_type', 'action_time', 'ip_address', 'user_agent', 'referer']
        }),
        ('行为数据', {
            'fields': ['action_data']
        }),
    ]


@admin.register(AbnormalBehavior)
class AbnormalBehaviorAdmin(admin.ModelAdmin):
    """异常行为记录管理员"""
    list_display = ['user', 'abnormal_type', 'risk_score', 'detected_time', 'is_warned', 'is_reported']
    list_filter = ['abnormal_type', 'detected_time', 'is_warned', 'is_reported']
    search_fields = ['user__username', 'abnormal_type']
    readonly_fields = ['detected_time']
    date_hierarchy = 'detected_time'
    fieldsets = [
        ('用户信息', {
            'fields': ['user']
        }),
        ('异常行为信息', {
            'fields': ['behavior', 'abnormal_type', 'risk_score', 'detected_time']
        }),
        ('处理状态', {
            'fields': ['is_warned', 'is_reported']
        }),
    ]


@admin.register(BehaviorConfig)
class BehaviorConfigAdmin(admin.ModelAdmin):
    """行为分析配置管理员"""
    list_display = ['config_key', 'config_value', 'description', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['config_key', 'description']
    fieldsets = [
        ('配置信息', {
            'fields': ['config_key', 'config_value', 'description']
        }),
        ('时间信息', {
            'fields': ['created_at', 'updated_at']
        }),
    ]


@admin.register(Warning)
class WarningAdmin(admin.ModelAdmin):
    """警告通知管理员"""
    list_display = ['user', 'warning_type', 'warning_time', 'is_read']
    list_filter = ['warning_type', 'warning_time', 'is_read']
    search_fields = ['user__username', 'warning_type', 'warning_content']
    readonly_fields = ['warning_time']
    date_hierarchy = 'warning_time'
    fieldsets = [
        ('用户信息', {
            'fields': ['user']
        }),
        ('警告信息', {
            'fields': ['warning_type', 'warning_content', 'warning_time']
        }),
        ('状态信息', {
            'fields': ['is_read']
        }),
    ]


@admin.register(BehaviorReport)
class BehaviorReportAdmin(admin.ModelAdmin):
    """异常行为报告管理员"""
    list_display = ['user', 'total_score', 'report_time', 'admin_status', 'processed_by', 'processed_at']
    list_filter = ['admin_status', 'report_time', 'processed_at']
    search_fields = ['user__username', 'report_content', 'admin_note']
    readonly_fields = ['report_time']
    date_hierarchy = 'report_time'
    fieldsets = [
        ('用户信息', {
            'fields': ['user']
        }),
        ('报告信息', {
            'fields': ['report_content', 'total_score', 'report_time']
        }),
        ('处理信息', {
            'fields': ['admin_status', 'admin_note', 'processed_by', 'processed_at']
        }),
    ]

    def save_model(self, request, obj, form, change):
        """保存模型时自动设置处理人和处理时间"""
        if obj.admin_status == 'resolved' or obj.admin_status == 'ignored':
            obj.processed_by = request.user
            obj.processed_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    """系统日志管理员"""
    list_display = ['log_time', 'log_level', 'log_type', 'user', 'description', 'ip_address']
    list_filter = ['log_level', 'log_type', 'log_time']
    search_fields = ['description', 'user__username', 'ip_address', 'request_path']
    readonly_fields = ['log_time', 'log_level', 'log_type', 'user', 'description', 'ip_address', 'user_agent', 'request_path', 'extra_data']
    date_hierarchy = 'log_time'
    fieldsets = [
        ('日志基本信息', {
            'fields': ['log_time', 'log_level', 'log_type']
        }),
        ('关联信息', {
            'fields': ['user', 'ip_address', 'user_agent', 'request_path']
        }),
        ('日志内容', {
            'fields': ['description', 'extra_data']
        }),
    ]

    def has_add_permission(self, request):
        """禁止手动添加日志"""
        return False

    def has_change_permission(self, request, obj=None):
        """禁止修改日志"""
        return False

    def has_delete_permission(self, request, obj=None):
        """只允许管理员删除日志"""
        return request.user.is_superuser