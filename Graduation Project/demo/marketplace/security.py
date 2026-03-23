"""
校园二手交易平台三层安全架构模块
包含身份安全、行为安全、数据安全三个层面
"""
import re
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import AbnormalBehavior, BehaviorReport, SecurityLog, UserBehavior


class SecurityValidator:
    """安全验证器 - 三层安全架构核心"""
    
    @staticmethod
    def validate_email_domain(email):
        """
        身份安全：验证校园邮箱域名
        仅允许特定域名的邮箱注册
        """
        allowed_domains = getattr(settings, 'ALLOWED_EMAIL_DOMAINS', [
            'edu.cn',
            'edu',
        ])
        
        if not allowed_domains:
            return True
        
        try:
            domain = email.split('@')[1].lower()
            for allowed_domain in allowed_domains:
                if domain.endswith(allowed_domain):
                    return True
            return False
        except:
            return False
    
    @staticmethod
    def validate_password_strength(password):
        """
        身份安全：验证密码强度
        要求：至少8位，包含大小写字母、数字、特殊字符
        """
        if len(password) < 8:
            return False, "密码长度至少需要8位"
        
        if not re.search(r'[a-z]', password):
            return False, "密码需要包含小写字母"
        
        if not re.search(r'[A-Z]', password):
            return False, "密码需要包含大写字母"
        
        if not re.search(r'\d', password):
            return False, "密码需要包含数字"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "密码需要包含特殊字符"
        
        return True, "密码强度合格"
    
    @staticmethod
    def detect_abnormal_login(user, request):
        """
        身份安全：检测异常登录行为
        """
        if not user or not user.is_authenticated:
            return False
        
        ip_address = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        is_abnormal = False
        risk_level = 'low'
        risk_description = ''
        
        # 1. 检测登录频率
        recent_logins = SecurityLog.objects.filter(
            user=user,
            log_type='login',
            created_at__gte=timezone.now() - timedelta(minutes=30)
        ).count()
        
        if recent_logins > 5:
            is_abnormal = True
            risk_level = 'high'
            risk_description = f'30分钟内登录{recent_logins}次，可能存在暴力破解尝试'
        
        # 2. 检测IP地址变化
        recent_ips = SecurityLog.objects.filter(
            user=user,
            log_type='login',
            created_at__gte=timezone.now() - timedelta(days=7)
        ).values_list('ip_address', flat=True).distinct()
        
        if ip_address and recent_ips and ip_address not in recent_ips:
            is_abnormal = True
            risk_level = 'medium'
            risk_description = f'新的IP地址登录: {ip_address}'
        
        # 3. 检测User-Agent变化
        recent_user_agents = SecurityLog.objects.filter(
            user=user,
            log_type='login',
            created_at__gte=timezone.now() - timedelta(days=7)
        ).values_list('user_agent', flat=True).distinct()
        
        if user_agent and recent_user_agents and user_agent not in recent_user_agents:
            if not is_abnormal:
                is_abnormal = True
                risk_level = 'low'
                risk_description = '新设备/浏览器登录'
        
        # 记录异常行为
        if is_abnormal:
            AbnormalBehavior.objects.create(
                user=user,
                behavior_type='abnormal_login',
                risk_level=risk_level,
                description=risk_description,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            SecurityLog.objects.create(
                user=user,
                log_type='suspicious',
                ip_address=ip_address,
                user_agent=user_agent,
                details=risk_description
            )
        
        return is_abnormal
    
    @staticmethod
    def detect_abnormal_behavior(user, action_type, action_data=None):
        """
        行为安全：检测异常行为模式
        """
        if not user or not user.is_authenticated:
            return False
        
        is_abnormal = False
        risk_level = 'low'
        risk_description = ''
        
        # 1. 检测短时间内高频操作
        recent_actions = UserBehavior.objects.filter(
            user=user,
            action_time__gte=timezone.now() - timedelta(minutes=5)
        ).count()
        
        if recent_actions > 50:
            is_abnormal = True
            risk_level = 'high'
            risk_description = f'5分钟内操作{recent_actions}次，可能存在机器人行为'
        
        # 2. 检测价格异常
        if action_type in ['create_product', 'update_product'] and action_data:
            try:
                price = float(action_data.get('price', 0))
                if price > 100000:
                    is_abnormal = True
                    risk_level = 'medium'
                    risk_description = f'商品价格异常高: ¥{price}'
            except:
                pass
        
        # 3. 检测敏感词（简化版）
        if action_type in ['create_product', 'send_message'] and action_data:
            sensitive_words = ['赌博', '诈骗', '违禁品', '枪支', '毒品']
            content = str(action_data)
            for word in sensitive_words:
                if word in content:
                    is_abnormal = True
                    risk_level = 'high'
                    risk_description = f'内容包含敏感词: {word}'
                    break
        
        # 记录异常行为
        if is_abnormal:
            AbnormalBehavior.objects.create(
                user=user,
                behavior_type=f'abnormal_{action_type}',
                risk_level=risk_level,
                description=risk_description
            )
            
            SecurityLog.objects.create(
                user=user,
                log_type='suspicious',
                details=risk_description
            )
        
        return is_abnormal
    
    @staticmethod
    def sanitize_user_input(input_data):
        """
        数据安全：用户输入消毒
        防止XSS、SQL注入等攻击
        """
        if not input_data:
            return input_data
        
        # 转换为字符串
        input_str = str(input_data)
        
        # 移除危险标签
        dangerous_tags = ['<script>', '</script>', '<iframe>', '</iframe>', '<img', 'javascript:']
        for tag in dangerous_tags:
            input_str = input_str.replace(tag, '')
        
        # 转义特殊字符
        input_str = input_str.replace('&', '&amp;')
        input_str = input_str.replace('<', '&lt;')
        input_str = input_str.replace('>', '&gt;')
        input_str = input_str.replace('"', '&quot;')
        input_str = input_str.replace("'", '&#x27;')
        
        return input_str
    
    @staticmethod
    def mask_sensitive_data(data, data_type='email'):
        """
        数据安全：敏感数据脱敏
        """
        if not data:
            return data
        
        if data_type == 'email':
            parts = data.split('@')
            if len(parts) == 2:
                username = parts[0]
                domain = parts[1]
                if len(username) > 2:
                    masked_username = username[:2] + '*' * (len(username) - 2)
                else:
                    masked_username = username + '*'
                return f'{masked_username}@{domain}'
        
        elif data_type == 'phone':
            if len(data) >= 11:
                return data[:3] + '****' + data[-4:]
        
        return data


def log_security_event(user, log_type, ip_address='', user_agent='', details=''):
    """记录安全事件"""
    try:
        SecurityLog.objects.create(
            user=user if user and user.is_authenticated else None,
            log_type=log_type,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
    except Exception as e:
        pass


def send_security_alert(user, alert_type, alert_message):
    """发送安全预警邮件"""
    if not user or not user.email:
        return False
    
    try:
        subject = f'【旧遇】安全预警: {alert_type}'
        message = f"""
        尊敬的用户 {user.username}：
        
        {alert_message}
        
        如非本人操作，请立即修改密码并联系客服。
        
        此致
        旧遇团队
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True
        )
        return True
    except Exception as e:
        return False
