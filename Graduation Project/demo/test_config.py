#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
校园二手交易平台测试配置文件
包含测试环境配置、测试数据配置、性能测试参数等
"""

import os

# 测试环境配置
TEST_CONFIG = {
    # 数据库配置
    'DATABASE': {
        'NAME': 'test_db.sqlite3',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'NAME': 'test_db.sqlite3',
        }
    },
    
    # 测试数据配置
    'TEST_DATA': {
        'NUM_USERS': 100,           # 测试用户数量
        'NUM_PRODUCTS': 200,        # 测试商品数量
        'NUM_CATEGORIES': 10,       # 测试分类数量
        'NUM_TRANSACTIONS': 50,     # 测试交易数量
    },
    
    # 性能测试配置
    'PERFORMANCE_TEST': {
        'CONCURRENT_THREADS': 10,   # 并发测试线程数
        'REQUESTS_PER_THREAD': 20,  # 每个线程请求数
        'LOAD_TEST_DURATION': 60,   # 负载测试持续时间(秒)
        'STRESS_TEST_MULTIPLIER': 3, # 压力测试倍数
    },
    
    # 功能测试配置
    'FUNCTIONAL_TEST': {
        'TEST_TIMEOUT': 30,         # 单个测试超时时间(秒)
        'RETRY_COUNT': 3,           # 失败重试次数
        'BROWSER': 'chrome',        # 浏览器类型(chrome/firefox)
        'HEADLESS': True,           # 是否无头模式
    },
    
    # 安全测试配置
    'SECURITY_TEST': {
        'PENETRATION_TEST_LEVEL': 'medium',  # 渗透测试级别(low/medium/high)
        'SQL_INJECTION_TESTS': True,         # 是否进行SQL注入测试
        'XSS_TESTS': True,                   # 是否进行XSS测试
        'CSRF_TESTS': True,                  # 是否进行CSRF测试
    },
    
    # API测试配置
    'API_TEST': {
        'BASE_URL': 'http://localhost:8000',
        'AUTH_TOKEN': 'test_token',
        'RATE_LIMIT': 100,          # API速率限制(请求/分钟)
        'TIMEOUT': 10,              # API请求超时时间(秒)
    },
    
    # 报告配置
    'REPORT': {
        'FORMAT': 'html',           # 报告格式(html/text/json)
        'OUTPUT_DIR': 'test_reports',  # 报告输出目录
        'INCLUDE_SCREENSHOTS': True,   # 是否包含截图
        'GENERATE_PDF': False,         # 是否生成PDF报告
    },
    
    # 邮件通知配置
    'NOTIFICATION': {
        'ENABLED': False,           # 是否启用邮件通知
        'SMTP_SERVER': 'smtp.example.com',
        'SMTP_PORT': 587,
        'FROM_EMAIL': 'tests@example.com',
        'TO_EMAILS': ['admin@example.com'],
    }
}

# 测试数据模板
TEST_DATA_TEMPLATES = {
    'USER': {
        'username': 'testuser_{index}',
        'email': 'testuser{index}@example.com',
        'password': 'TestPassword123!',
        'first_name': 'Test',
        'last_name': 'User{index}'
    },
    
    'PRODUCT': {
        'name': '测试商品_{index}',
        'description': '这是第{index}个测试商品的描述',
        'price': 50.0,
        'condition': 'excellent',
        'location': '测试地点'
    },
    
    'CATEGORY': {
        'name': '测试分类_{index}',
        'description': '这是第{index}个测试分类的描述'
    },
    
    'TRANSACTION': {
        'status': 'pending',
        'buyer_message': '我想购买这个商品',
        'offer_price': 45.0
    }
}

# 性能基准指标
PERFORMANCE_BENCHMARKS = {
    'DATABASE': {
        'CONNECTION_TIME': 0.1,     # 数据库连接时间上限(秒)
        'QUERY_TIME': 0.5,          # 查询时间上限(秒)
        'WRITE_TIME': 0.3,          # 写入时间上限(秒)
    },
    
    'API': {
        'LOGIN_TIME': 1.0,          # 登录时间上限(秒)
        'PAGE_LOAD_TIME': 2.0,      # 页面加载时间上限(秒)
        'SEARCH_TIME': 1.5,         # 搜索时间上限(秒)
    },
    
    'CONCURRENT': {
        'AVG_RESPONSE_TIME': 1.0,   # 平均响应时间上限(秒)
        'MAX_RESPONSE_TIME': 3.0,   # 最大响应时间上限(秒)
        'REQUESTS_PER_SECOND': 10,  # 最低每秒请求数
    },
    
    'MEMORY': {
        'MAX_USAGE_MB': 500,        # 最大内存使用量(MB)
        'MEMORY_LEAK_THRESHOLD': 50, # 内存泄漏阈值(MB)
    }
}

# 测试用例优先级
TEST_PRIORITY = {
    'CRITICAL': ['用户认证', '交易流程', '支付安全'],
    'HIGH': ['商品管理', '搜索功能', '消息系统'],
    'MEDIUM': ['用户行为分析', '推荐系统', '安全日志'],
    'LOW': ['界面样式', '性能优化', '辅助功能']
}

# 测试环境检查清单
ENVIRONMENT_CHECKLIST = {
    'DATABASE': [
        '数据库连接正常',
        '表结构完整',
        '索引优化',
        '备份机制'
    ],
    'SERVER': [
        'Web服务器运行正常',
        '静态文件服务',
        '缓存配置',
        '负载均衡'
    ],
    'SECURITY': [
        'HTTPS配置',
        '防火墙设置',
        '访问控制',
        '日志监控'
    ],
    'NETWORK': [
        '网络连通性',
        'DNS解析',
        '端口开放',
        '带宽监控'
    ]
}


def get_test_config():
    """获取测试配置"""
    return TEST_CONFIG


def get_performance_benchmarks():
    """获取性能基准指标"""
    return PERFORMANCE_BENCHMARKS


def generate_test_data(template_type, index, **kwargs):
    """生成测试数据"""
    template = TEST_DATA_TEMPLATES.get(template_type, {})
    data = {}
    
    for key, value in template.items():
        if isinstance(value, str) and '{index}' in value:
            data[key] = value.format(index=index)
        else:
            data[key] = value
    
    # 更新自定义参数
    data.update(kwargs)
    
    return data


def check_environment():
    """检查测试环境"""
    issues = []
    
    # 检查数据库连接
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        issues.append(f"数据库连接失败: {e}")
    
    # 检查静态文件目录
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if not os.path.exists(static_dir):
        issues.append("静态文件目录不存在")
    
    # 检查媒体文件目录
    media_dir = os.path.join(os.path.dirname(__file__), 'media')
    if not os.path.exists(media_dir):
        issues.append("媒体文件目录不存在")
    
    return issues


if __name__ == "__main__":
    # 测试配置功能
    print("测试配置检查:")
    issues = check_environment()
    
    if issues:
        print("发现以下问题:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("环境检查通过")
    
    # 显示配置信息
    print(f"\n测试数据配置:")
    print(f"  用户数量: {TEST_CONFIG['TEST_DATA']['NUM_USERS']}")
    print(f"  商品数量: {TEST_CONFIG['TEST_DATA']['NUM_PRODUCTS']}")
    print(f"  并发线程: {TEST_CONFIG['PERFORMANCE_TEST']['CONCURRENT_THREADS']}")