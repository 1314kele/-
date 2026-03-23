from .models import UserBehavior, AbnormalBehavior, BehaviorConfig, Warning, BehaviorReport
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import re
from user_agents import parse
import numpy as np

User = get_user_model()

class AbnormalBehaviorAnalyzer:
    """
    异常行为分析器
    负责识别用户的异常行为模式
    """
    
    def __init__(self):
        """
        初始化异常行为分析器，加载配置参数
        """
        self.config = self.load_config()
    
    def load_config(self):
        """
        加载系统配置参数
        """
        config = {
            # 默认配置值
            'login_frequency_threshold': 5,  # 5分钟内登录失败次数阈值
            'operation_frequency_threshold': 100,  # 1分钟内操作次数阈值
            'transaction_amount_threshold': 5000,  # 单次交易金额阈值
            'transaction_frequency_threshold': 10,  # 1小时内交易次数阈值
            'warning_threshold': 50,  # 警告阈值
            'report_threshold': 100,  # 上报阈值
            'login_risk_score': 20,  # 异常登录风险分值
            'frequency_risk_score': 30,  # 异常操作频率风险分值
            'transaction_risk_score': 40,  # 异常交易金额风险分值
            'automation_risk_score': 50,  # 脚本自动化操作风险分值
        }
        
        # 从数据库加载配置，覆盖默认值
        try:
            for key, default_value in config.items():
                config_obj = BehaviorConfig.objects.filter(config_key=key).first()
                if config_obj:
                    try:
                        config[key] = int(config_obj.config_value)
                    except ValueError:
                        config[key] = default_value
        except Exception:
            pass
        
        return config
    
    def analyze_behavior(self, behavior):
        """
        分析单个用户行为，识别异常
        """
        user = behavior.user
        abnormal_behaviors = []
        
        # 检查异常登录
        if behavior.action_type == 'login':
            if self.detect_abnormal_login(user, behavior):
                abnormal_behaviors.append({
                    'type': 'login',
                    'score': self.config['login_risk_score'],
                    'reason': '异常登录行为'
                })
        
        # 检查异常操作频率
        if self.detect_abnormal_operation_frequency(user, behavior):
            abnormal_behaviors.append({
                'type': 'frequency',
                'score': self.config['frequency_risk_score'],
                'reason': '异常操作频率'
            })
        
        # 检查异常交易金额
        if behavior.action_type == 'transaction':
            if self.detect_abnormal_transaction(user, behavior):
                abnormal_behaviors.append({
                    'type': 'transaction',
                    'score': self.config['transaction_risk_score'],
                    'reason': '异常交易金额或频率'
                })
        
        # 检查脚本自动化操作
        if self.detect_automation_operation(behavior):
            abnormal_behaviors.append({
                'type': 'automation',
                'score': self.config['automation_risk_score'],
                'reason': '疑似脚本自动化操作'
            })
        
        # 记录异常行为
        for ab in abnormal_behaviors:
            AbnormalBehavior.objects.create(
                user=user,
                behavior=behavior,
                abnormal_type=ab['type'],
                risk_score=ab['score']
            )
        
        # 检查是否需要警告或上报
        self.check_warning_and_report(user)
    
    def detect_abnormal_login(self, user, behavior):
        """
        检测异常登录行为
        """
        # 1. 检查登录失败频率
        time_threshold = datetime.now() - timedelta(minutes=5)
        failed_logins = UserBehavior.objects.filter(
            user=user,
            action_type='login',
            action_time__gte=time_threshold,
            action_data__contains={'login_failed': True}
        ).count()
        
        if failed_logins >= self.config['login_frequency_threshold']:
            return True
        
        # 2. 检查登录IP地址是否异常（简化实现，实际可结合IP地理位置库）
        # 这里仅做示例，实际项目中可集成IP地理位置API
        ip_address = behavior.ip_address
        if re.match(r'^192\.168\.|^10\.|^172\.(1[6-9]|2[0-9]|3[0-1])\.', ip_address):
            # 私有IP地址，视为正常
            return False
        
        # 3. 检查设备信息是否异常
        user_agent = parse(behavior.user_agent)
        if user_agent.is_bot:
            return True
        
        return False
    
    def detect_abnormal_operation_frequency(self, user, behavior):
        """
        检测异常操作频率
        """
        # 检查1分钟内的操作次数
        time_threshold = datetime.now() - timedelta(minutes=1)
        recent_operations = UserBehavior.objects.filter(
            user=user,
            action_time__gte=time_threshold
        ).count()
        
        if recent_operations >= self.config['operation_frequency_threshold']:
            return True
        
        return False
    
    def detect_abnormal_transaction(self, user, behavior):
        """
        检测异常交易行为
        """
        # 获取交易金额
        transaction_amount = behavior.action_data.get('amount', 0)
        try:
            transaction_amount = float(transaction_amount)
        except (ValueError, TypeError):
            transaction_amount = 0
        
        # 1. 检查单次交易金额是否超过阈值
        if transaction_amount > self.config['transaction_amount_threshold']:
            return True
        
        # 2. 检查1小时内的交易次数
        time_threshold = datetime.now() - timedelta(hours=1)
        recent_transactions = UserBehavior.objects.filter(
            user=user,
            action_type='transaction',
            action_time__gte=time_threshold
        ).count()
        
        if recent_transactions >= self.config['transaction_frequency_threshold']:
            return True
        
        return False
    
    def detect_automation_operation(self, behavior):
        """
        检测脚本自动化操作
        """
        user_agent = behavior.user_agent
        
        # 1. 检查是否为常见爬虫/自动化工具
        bot_keywords = ['bot', 'crawler', 'spider', 'scraper', 'automation', 'selenium', 'webdriver']
        if any(keyword in user_agent.lower() for keyword in bot_keywords):
            return True
        
        # 2. 检查请求头是否异常（简化实现）
        if not user_agent or len(user_agent) < 10:
            return True
        
        # 3. 检查行为数据中的异常模式
        action_data = behavior.action_data
        if isinstance(action_data, dict):
            # 检查是否有自动化工具特征
            if 'selenium' in str(action_data).lower() or 'webdriver' in str(action_data).lower():
                return True
        
        return False
    
    def calculate_user_risk_score(self, user):
        """
        计算用户的风险总分值
        """
        # 获取最近7天的异常行为
        time_threshold = datetime.now() - timedelta(days=7)
        abnormal_behaviors = AbnormalBehavior.objects.filter(
            user=user,
            detected_time__gte=time_threshold
        )
        
        # 计算总分
        total_score = sum(ab.risk_score for ab in abnormal_behaviors)
        
        return total_score
    
    def check_warning_and_report(self, user):
        """
        检查是否需要发送警告或上报管理员
        """
        total_score = self.calculate_user_risk_score(user)
        
        # 检查是否需要上报管理员
        if total_score >= self.config['report_threshold']:
            # 检查是否已经上报过
            report = BehaviorReport.objects.filter(
                user=user,
                admin_status__in=['pending', 'processing']
            ).first()
            
            if not report:
                # 创建异常行为报告
                recent_abnormal = AbnormalBehavior.objects.filter(
                    user=user,
                    detected_time__gte=datetime.now() - timedelta(days=7)
                ).order_by('-detected_time')[:10]
                
                report_content = f"用户{user.username}的异常行为总分达到{total_score}，超过上报阈值{self.config['report_threshold']}。\n"
                report_content += "最近10条异常行为：\n"
                for ab in recent_abnormal:
                    report_content += f"- {ab.get_abnormal_type_display()}：{ab.risk_score}分 ({ab.detected_time.strftime('%Y-%m-%d %H:%M:%S')})\n"
                
                BehaviorReport.objects.create(
                    user=user,
                    report_content=report_content,
                    total_score=total_score
                )
        
        # 检查是否需要发送警告
        elif total_score >= self.config['warning_threshold']:
            # 检查是否已经发送过警告
            warning = Warning.objects.filter(
                user=user,
                is_read=False
            ).first()
            
            if not warning:
                # 创建警告通知
                Warning.objects.create(
                    user=user,
                    warning_type='risk_threshold',
                    warning_content=f"您的账号存在异常行为，风险总分达到{total_score}，请规范您的操作行为。"
                )
    
    def analyze_all_users(self):
        """
        分析所有用户的行为，识别异常
        可定期调用（如每小时）
        """
        # 获取最近1小时的用户行为
        time_threshold = datetime.now() - timedelta(hours=1)
        recent_behaviors = UserBehavior.objects.filter(
            action_time__gte=time_threshold
        )
        
        # 按用户分组分析
        user_behaviors = {}
        for behavior in recent_behaviors:
            user = behavior.user
            if user not in user_behaviors:
                user_behaviors[user] = []
            user_behaviors[user].append(behavior)
        
        # 分析每个用户的行为
        for user, behaviors in user_behaviors.items():
            for behavior in behaviors:
                self.analyze_behavior(behavior)
    
    def update_config(self, config_updates):
        """
        更新配置参数
        """
        for key, value in config_updates.items():
            if key in self.config:
                self.config[key] = value
                # 保存到数据库
                try:
                    config_obj, created = BehaviorConfig.objects.get_or_create(
                        config_key=key,
                        defaults={'config_value': str(value), 'description': ''}
                    )
                    if not created:
                        config_obj.config_value = str(value)
                        config_obj.save()
                except Exception:
                    pass
