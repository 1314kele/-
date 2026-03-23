from django.utils.deprecation import MiddlewareMixin
from .models import UserBehavior
from django.contrib.auth import get_user_model
from django.urls import resolve
import json

User = get_user_model()

class UserBehaviorMiddleware(MiddlewareMixin):
    """
    用户行为采集中间件
    捕获并记录用户在平台上的各类操作行为
    """
    
    def process_request(self, request):
        """
        在请求处理前记录用户行为
        """
        # 跳过静态文件和媒体文件的请求
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None
        
        # 跳过管理员页面的请求
        if request.path.startswith('/admin/'):
            return None
        
        # 尝试获取当前用户
        user = request.user if request.user.is_authenticated else None
        
        # 提取请求信息
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referer = request.META.get('HTTP_REFERER', '')
        session_id = request.session.session_key if hasattr(request.session, 'session_key') else ''
        
        # 解析请求路径，获取视图名称
        try:
            resolved_url = resolve(request.path_info)
            view_name = resolved_url.view_name
        except Exception:
            view_name = 'unknown'
        
        # 确定行为类型
        action_type = self.get_action_type(request, view_name)
        
        # 提取行为数据
        action_data = self.get_action_data(request, view_name)
        
        # 记录行为数据
        if user is not None:
            UserBehavior.objects.create(
                user=user,
                action_type=action_type,
                ip_address=ip_address,
                user_agent=user_agent,
                referer=referer,
                action_data=action_data,
                session_id=session_id
            )
        
        return None
    
    def get_client_ip(self, request):
        """
        获取客户端真实IP地址
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_action_type(self, request, view_name):
        """
        根据请求类型和视图名称确定行为类型
        """
        # 登录行为
        if view_name in ['login', 'auth_login'] or request.path in ['/accounts/login/', '/login/']:
            return 'login'
        
        # 登出行为
        if view_name in ['logout', 'auth_logout'] or request.path in ['/accounts/logout/', '/logout/']:
            return 'logout'
        
        # 交易相关行为
        if 'transaction' in view_name or 'order' in view_name:
            return 'transaction'
        
        # 收藏行为
        if 'favorite' in view_name:
            return 'favorite'
        
        # 消息相关行为
        if 'message' in view_name:
            return 'message'
        
        # 评价行为
        if 'review' in view_name:
            return 'review'
        
        # 表单提交行为
        if request.method in ['POST', 'PUT', 'DELETE']:
            return 'submit'
        
        # 点击行为（GET请求但带有特定参数）
        if request.method == 'GET' and ('action' in request.GET or 'click' in request.GET):
            return 'click'
        
        # 默认浏览行为
        return 'browse'
    
    def get_action_data(self, request, view_name):
        """
        提取行为相关的数据
        """
        action_data = {
            'path': request.path,
            'method': request.method,
            'view_name': view_name,
            'query_params': dict(request.GET)
        }
        
        # 对于POST请求，尝试获取表单数据
        if request.method == 'POST':
            try:
                if request.content_type == 'application/json':
                    action_data['post_data'] = json.loads(request.body)
                else:
                    action_data['post_data'] = dict(request.POST)
            except Exception:
                action_data['post_data'] = '无法解析的POST数据'
        
        return action_data
