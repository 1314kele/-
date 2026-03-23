from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# 知识图谱相关模型
class Knowledge(models.Model):
    """知识库条目"""
    KNOWLEDGE_TYPES = [
        ('faq', '常见问题'),
        ('rule', '平台规则'),
        ('tip', '交易技巧'),
        ('other', '其他'),
    ]
    
    knowledge_type = models.CharField(max_length=20, choices=KNOWLEDGE_TYPES, verbose_name='知识类型')
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    keywords = models.CharField(max_length=200, blank=True, verbose_name='关键词')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '知识库'
        verbose_name_plural = '知识库'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

# 推荐系统相关模型
class UserPreference(models.Model):
    """用户偏好"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='preferences', verbose_name='用户')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name='分类')
    preference_score = models.FloatField(default=0.0, verbose_name='偏好分数')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户偏好'
        verbose_name_plural = '用户偏好'
        unique_together = ('user', 'category')
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name}"

class ProductSimilarity(models.Model):
    """商品相似度"""
    product1 = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='similar_products1', verbose_name='商品1')
    product2 = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='similar_products2', verbose_name='商品2')
    similarity_score = models.FloatField(default=0.0, verbose_name='相似度分数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '商品相似度'
        verbose_name_plural = '商品相似度'
        unique_together = ('product1', 'product2')
    
    def __str__(self):
        return f"{self.product1.title} - {self.product2.title} ({self.similarity_score})"

class RecommendationLog(models.Model):
    """推荐日志"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendation_logs', verbose_name='用户')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='商品')
    recommendation_type = models.CharField(max_length=20, verbose_name='推荐类型')
    score = models.FloatField(verbose_name='推荐分数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '推荐日志'
        verbose_name_plural = '推荐日志'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.title}"

# 安全管理相关模型
class TwoFactorAuth(models.Model):
    """双因素认证"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    is_enabled = models.BooleanField(default=False, verbose_name='是否启用')
    secret_key = models.CharField(max_length=100, blank=True, null=True, verbose_name='密钥')
    recovery_codes = models.TextField(blank=True, null=True, verbose_name='恢复代码')
    last_used = models.DateTimeField(null=True, blank=True, verbose_name='最后使用时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '双因素认证'
        verbose_name_plural = '双因素认证'
    
    def __str__(self):
        return f"{self.user.username} - {'已启用' if self.is_enabled else '未启用'}"

class SecurityLog(models.Model):
    """安全日志"""
    LOG_TYPES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('2fa_setup', '双因素认证设置'),
        ('2fa_verify', '双因素认证验证'),
        ('password_change', '密码修改'),
        ('suspicious', '可疑操作'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_logs', verbose_name='用户')
    log_type = models.CharField(max_length=20, choices=LOG_TYPES, verbose_name='日志类型')
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    user_agent = models.TextField(verbose_name='用户代理')
    details = models.TextField(blank=True, verbose_name='详细信息')
    is_successful = models.BooleanField(default=True, verbose_name='是否成功')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '安全日志'
        verbose_name_plural = '安全日志'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_log_type_display()}"

class EncryptedData(models.Model):
    """加密数据"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='encrypted_data', verbose_name='用户')
    data_type = models.CharField(max_length=50, verbose_name='数据类型')
    encrypted_value = models.TextField(verbose_name='加密值')
    iv = models.CharField(max_length=100, blank=True, null=True, verbose_name='初始化向量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '加密数据'
        verbose_name_plural = '加密数据'
    
    def __str__(self):
        return f"{self.user.username} - {self.data_type}"

# 用户行为分析系统相关模型

class Category(models.Model):
    """商品分类"""
    name = models.CharField(max_length=100, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = '商品分类'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """二手商品"""
    STATUS_CHOICES = [
        ('available', '可交易'),
        ('sold', '已售出'),
        ('reserved', '已预订'),
    ]
    
    CONDITION_CHOICES = [
        ('new', '全新'),
        ('like_new', '几乎全新'),
        ('good', '良好'),
        ('fair', '一般'),
        ('poor', '较差'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='商品标题')
    description = models.TextField(verbose_name='商品描述')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='分类')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', verbose_name='卖家')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, verbose_name='商品状况')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name='交易状态')
    location = models.CharField(max_length=100, verbose_name='交易地点')
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name='纬度')
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name='经度')
    contact_info = models.CharField(max_length=200, verbose_name='联系方式')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='商品图片')
    views = models.PositiveIntegerField(default=0, verbose_name='浏览次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '二手商品'
        verbose_name_plural = '二手商品'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Favorite(models.Model):
    """收藏夹"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='用户')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')
    
    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        unique_together = ('user', 'product')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} 收藏了 {self.product.title}"

class Message(models.Model):
    """用户间消息"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='发送者')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name='接收者')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='相关商品')
    content = models.TextField(verbose_name='消息内容')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    
    class Meta:
        verbose_name = '消息'
        verbose_name_plural = '消息'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"

class Review(models.Model):
    """用户评价"""
    RATING_CHOICES = [
        (1, '★'),
        (2, '★★'),
        (3, '★★★'),
        (4, '★★★★'),
        (5, '★★★★★'),
    ]
    
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews', verbose_name='评价者')
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews', verbose_name='被评价者')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='相关商品')
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='评分')
    comment = models.TextField(verbose_name='评价内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评价时间')
    
    class Meta:
        verbose_name = '评价'
        verbose_name_plural = '评价'
        unique_together = ('reviewer', 'product')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.reviewer.username} 对 {self.reviewed_user.username} 的评价"

class Transaction(models.Model):
    """交易记录"""
    STATUS_CHOICES = [
        ('pending', '待确认'),
        ('confirmed', '已确认'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases', verbose_name='买家')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales', verbose_name='卖家')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='交易价格')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='交易状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='确认时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        verbose_name = '交易记录'
        verbose_name_plural = '交易记录'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.buyer.username} 购买 {self.product.title}"
    
    def confirm_transaction(self):
        """确认交易"""
        if self.status == 'pending':
            self.status = 'confirmed'
            self.confirmed_at = timezone.now()
            self.save()
    
    def complete_transaction(self):
        """完成交易"""
        if self.status == 'confirmed':
            self.status = 'completed'
            self.completed_at = timezone.now()
            # 同时更新商品状态为已售出
            self.product.status = 'sold'
            self.product.save()
            self.save()


class UserBehavior(models.Model):
    """用户行为数据"""
    ACTION_TYPES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('browse', '浏览'),
        ('click', '点击'),
        ('submit', '提交表单'),
        ('transaction', '交易'),
        ('favorite', '收藏'),
        ('message', '发送消息'),
        ('review', '评价'),
        ('other', '其他'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='behaviors', verbose_name='用户')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, verbose_name='行为类型')
    action_time = models.DateTimeField(auto_now_add=True, verbose_name='行为时间')
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    user_agent = models.TextField(verbose_name='用户代理')
    referer = models.URLField(blank=True, null=True, verbose_name='来源URL')
    action_data = models.TextField(blank=True, null=True, verbose_name='行为数据')
    session_id = models.CharField(max_length=100, verbose_name='会话ID')
    
    class Meta:
        verbose_name = '用户行为'
        verbose_name_plural = '用户行为'
        ordering = ['-action_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} - {self.action_time}"


class AbnormalBehavior(models.Model):
    """异常行为记录"""
    ABNORMAL_TYPES = [
        ('login', '异常登录'),
        ('frequency', '异常操作频率'),
        ('transaction', '异常交易金额'),
        ('automation', '脚本自动化操作'),
        ('other', '其他异常'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='abnormal_behaviors', verbose_name='用户')
    behavior = models.ForeignKey(UserBehavior, on_delete=models.CASCADE, verbose_name='关联行为')
    abnormal_type = models.CharField(max_length=20, choices=ABNORMAL_TYPES, verbose_name='异常类型')
    risk_score = models.IntegerField(default=0, verbose_name='风险分值')
    detected_time = models.DateTimeField(auto_now_add=True, verbose_name='检测时间')
    is_warned = models.BooleanField(default=False, verbose_name='已发送警告')
    is_reported = models.BooleanField(default=False, verbose_name='已上报管理员')
    
    class Meta:
        verbose_name = '异常行为'
        verbose_name_plural = '异常行为'
        ordering = ['-detected_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_abnormal_type_display()} - {self.risk_score}分"


class BehaviorConfig(models.Model):
    """系统配置"""
    id = models.BigAutoField(primary_key=True)
    config_key = models.CharField(max_length=100, unique=True, verbose_name='配置键')
    config_value = models.CharField(max_length=200, verbose_name='配置值')
    description = models.TextField(blank=True, verbose_name='配置描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '行为分析配置'
        verbose_name_plural = '行为分析配置'
        ordering = ['config_key']
    
    def __str__(self):
        return f"{self.config_key}: {self.config_value}"


class Warning(models.Model):
    """警告通知"""
    WARNING_TYPES = [
        ('abnormal_behavior', '异常行为警告'),
        ('risk_threshold', '风险阈值警告'),
        ('other', '其他警告'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='warnings', verbose_name='用户')
    warning_type = models.CharField(max_length=20, choices=WARNING_TYPES, verbose_name='警告类型')
    warning_content = models.TextField(verbose_name='警告内容')
    warning_time = models.DateTimeField(auto_now_add=True, verbose_name='警告时间')
    is_read = models.BooleanField(default=False, verbose_name='已读')
    
    class Meta:
        verbose_name = '警告通知'
        verbose_name_plural = '警告通知'
        ordering = ['-warning_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_warning_type_display()}"


class BehaviorReport(models.Model):
    """异常行为报告"""
    ADMIN_STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('resolved', '已解决'),
        ('ignored', '已忽略'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='behavior_reports', verbose_name='用户')
    report_content = models.TextField(verbose_name='报告内容')
    total_score = models.IntegerField(verbose_name='累计风险分数')
    report_time = models.DateTimeField(auto_now_add=True, verbose_name='报告时间')
    admin_status = models.CharField(max_length=20, choices=ADMIN_STATUS_CHOICES, default='pending', verbose_name='处理状态')
    admin_note = models.TextField(blank=True, verbose_name='管理员备注')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_reports', verbose_name='处理人')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')
    
    class Meta:
        verbose_name = '异常行为报告'
        verbose_name_plural = '异常行为报告'
        ordering = ['-report_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.total_score}分 - {self.get_admin_status_display()}"


class SystemLog(models.Model):
    """
    系统日志
    记录所有异常行为识别过程、预警通知、管理员操作等关键事件
    """
    LOG_LEVEL_CHOICES = [
        ('info', '信息'),
        ('warning', '警告'),
        ('error', '错误'),
        ('critical', '严重'),
    ]
    
    LOG_TYPE_CHOICES = [
        ('abnormal_behavior', '异常行为识别'),
        ('warning_notification', '警告通知'),
        ('report_submission', '异常报告提交'),
        ('admin_action', '管理员操作'),
        ('system_event', '系统事件'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    log_time = models.DateTimeField(auto_now_add=True, verbose_name='日志时间')
    log_level = models.CharField(max_length=20, choices=LOG_LEVEL_CHOICES, default='info', verbose_name='日志级别')
    log_type = models.CharField(max_length=50, choices=LOG_TYPE_CHOICES, verbose_name='日志类型')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='相关用户')
    description = models.TextField(verbose_name='日志描述')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(null=True, blank=True, verbose_name='用户代理')
    request_path = models.CharField(max_length=200, null=True, blank=True, verbose_name='请求路径')
    extra_data = models.TextField(null=True, blank=True, verbose_name='附加数据')
    
    class Meta:
        verbose_name = '系统日志'
        verbose_name_plural = '系统日志'
        ordering = ['-log_time']
    
    def __str__(self):
        return f"{self.get_log_level_display()} - {self.get_log_type_display()} - {self.log_time}"

class Notification(models.Model):
    """实时通知"""
    NOTIFICATION_TYPES = [
        ('message', '新消息'),
        ('transaction', '交易更新'),
        ('favorite', '收藏通知'),
        ('review', '新评价'),
        ('system', '系统通知'),
        ('security', '安全警告'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='用户')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, verbose_name='通知类型')
    title = models.CharField(max_length=200, verbose_name='通知标题')
    content = models.TextField(verbose_name='通知内容')
    link = models.URLField(blank=True, null=True, verbose_name='相关链接')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '实时通知'
        verbose_name_plural = '实时通知'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class Wallet(models.Model):
    """用户钱包"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet', verbose_name='用户')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='余额')
    frozen_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='冻结余额')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户钱包'
        verbose_name_plural = '用户钱包'
    
    def __str__(self):
        return f"{self.user.username} - ¥{self.balance}"

class WalletTransaction(models.Model):
    """钱包交易记录"""
    TRANSACTION_TYPES = [
        ('recharge', '充值'),
        ('withdraw', '提现'),
        ('payment', '支付'),
        ('refund', '退款'),
        ('income', '收入'),
        ('freeze', '冻结'),
        ('unfreeze', '解冻'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ]
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions', verbose_name='钱包')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name='交易类型')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='金额')
    balance_before = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='交易前余额')
    balance_after = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='交易后余额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    description = models.TextField(blank=True, verbose_name='描述')
    related_transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联交易')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '钱包交易记录'
        verbose_name_plural = '钱包交易记录'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - ¥{self.amount}"

class Payment(models.Model):
    """支付记录"""
    PAYMENT_METHODS = [
        ('wallet', '钱包支付'),
        ('alipay', '支付宝'),
        ('wechat', '微信支付'),
        ('bank', '银行卡'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('refunded', '已退款'),
    ]
    
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='payments', verbose_name='关联交易')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name='支付方式')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='支付金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    third_party_transaction_id = models.CharField(max_length=100, blank=True, verbose_name='第三方交易ID')
    payment_time = models.DateTimeField(null=True, blank=True, verbose_name='支付时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '支付记录'
        verbose_name_plural = '支付记录'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.get_payment_method_display()} - ¥{self.amount}"