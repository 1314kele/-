import re

with open('论文终稿9.0_扩充第三章版.txt', 'r', encoding='gbk') as f:
    text = f.read()

old_str = """　　　核心代码实现如下：
　　　
　　　
　　　
　　　
　　　
　　　"""

code_snippet = """　　　核心代码实现如下：
```python
class SecurityValidator:
    \"\"\"安全验证器 - 三层安全防护架构核心\"\"\"

    @staticmethod
    def validate_email_domain(email):
        \"\"\"【1. 身份安全层】验证校园edu邮箱，从源头防止外部人员黑产\"\"\"
        allowed_domains = ['edu.cn', 'edu']
        try:
            domain = email.split('@')[1].lower()
            return any(domain.endswith(d) for d in allowed_domains)
        except IndexError:
            return False

    @staticmethod
    def detect_abnormal_login(user, request):
        \"\"\"【2. 行为安全层】检测异地登录与高频登录异常\"\"\"
        recent_logs = SecurityLog.objects.filter(
            user=user, 
            log_type='login'
        ).order_by('-timestamp')[:5]
        
        # 提取IP进行比对，若出现IP高频切换或非常用地登录，触发预警机制
        if is_ip_anomalous:
            AbnormalBehavior.objects.create(
                user=user, behavior_type='abnormal_login', risk_level='high'
            )
            return True
        return False

    @staticmethod
    def mask_sensitive_data(data, data_type='email'):
        \"\"\"【3. 数据安全层】用户隐私数据脱敏处理\"\"\"
        if not data: return data
        if data_type == 'email':
            parts = data.split('@')
            if len(parts[0]) > 3:
                return f"{parts[0][:3]}***@{parts[1]}"
            return f"***@{parts[1]}"
        return data
```"""

new_text = text.replace(old_str, code_snippet)

with open('论文终稿9.0_扩充第三章版.txt', 'w', encoding='gbk') as f:
    f.write(new_text)

if text != new_text:
    print('Replaced successfully!')
else:
    print('Failed to replace! String might not match.')
