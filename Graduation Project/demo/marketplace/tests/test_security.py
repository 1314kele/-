from django.test import TestCase
from django.contrib.auth.models import User
from ..models import TwoFactorAuth, SecurityLog, EncryptedData
from ..security import security_manager

class SecurityTest(TestCase):
    """安全管理模块测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
    
    def test_two_factor_auth_setup(self):
        """测试双因素认证设置"""
        # 生成2FA密钥
        result = security_manager.generate_2fa_secret(self.user)
        
        # 检查结果
        self.assertIn('secret', result)
        self.assertIn('qr_code_url', result)
        self.assertIn('recovery_codes', result)
        self.assertEqual(len(result['recovery_codes']), 10)
        
        # 检查双因素认证记录是否创建
        two_factor = TwoFactorAuth.objects.get(user=self.user)
        self.assertEqual(two_factor.secret_key, result['secret'])
        self.assertFalse(two_factor.is_enabled)
    
    def test_security_logging(self):
        """测试安全日志记录"""
        # 记录安全事件
        security_manager.log_security_event(
            user=self.user,
            log_type='login',
            ip_address='127.0.0.1',
            user_agent='test user agent',
            details='测试登录',
            is_successful=True
        )
        
        # 检查日志是否创建
        logs = SecurityLog.objects.filter(user=self.user)
        self.assertEqual(logs.count(), 1)
        log = logs.first()
        self.assertEqual(log.log_type, 'login')
        self.assertEqual(log.ip_address, '127.0.0.1')
        self.assertEqual(log.user_agent, 'test user agent')
        self.assertEqual(log.details, '测试登录')
        self.assertTrue(log.is_successful)
    
    def test_data_encryption(self):
        """测试数据加密"""
        test_data = '测试加密数据'
        
        # 加密数据
        encrypted = security_manager.encrypt_data(test_data)
        self.assertIn('encrypted_value', encrypted)
        self.assertIn('iv', encrypted)
        
        # 解密数据
        decrypted = security_manager.decrypt_data(
            encrypted['encrypted_value'],
            encrypted['iv']
        )
        self.assertEqual(decrypted, test_data)
    
    def test_encrypted_data_storage(self):
        """测试加密数据存储"""
        test_data = '测试存储数据'
        data_type = 'test_data'
        
        # 存储加密数据
        result = security_manager.store_encrypted_data(
            user=self.user,
            data_type=data_type,
            data=test_data
        )
        self.assertTrue(result)
        
        # 获取加密数据
        retrieved_data = security_manager.get_encrypted_data(
            user=self.user,
            data_type=data_type
        )
        self.assertEqual(retrieved_data, test_data)
    
    def test_security_summary(self):
        """测试安全摘要"""
        # 获取安全摘要
        summary = security_manager.get_security_summary(self.user)
        
        # 检查摘要数据
        self.assertIn('two_factor_enabled', summary)
        self.assertIn('recent_logs', summary)
        self.assertIn('suspicious_count', summary)
        self.assertFalse(summary['two_factor_enabled'])
        self.assertEqual(summary['suspicious_count'], 0)