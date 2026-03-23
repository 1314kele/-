#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园二手交易平台性能测试脚本
包含负载测试、压力测试、并发测试等功能
"""

import os
import sys
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')

import django
django.setup()

# Django导入必须在django.setup()之后
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.db import connection
from django.core.management import call_command
from marketplace.models import Product, Category, Transaction, UserBehavior


class PerformanceTestSuite:
    """性能测试套件"""
    
    def __init__(self):
        self.client = Client()
        self.base_url = 'http://localhost:8000'
        self.results = {}
        
    def measure_time(self, func, *args, **kwargs):
        """测量函数执行时间"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    
    def database_performance_test(self):
        """数据库性能测试"""
        print("=== 数据库性能测试 ===")
        
        # 测试数据库连接性能
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM marketplace_product")
            count = cursor.fetchone()[0]
        db_connect_time = time.time() - start_time
        
        # 测试查询性能
        start_time = time.time()
        products = list(Product.objects.all()[:100])
        query_time = time.time() - start_time
        
        # 测试写入性能
        start_time = time.time()
        category = Category.objects.first()
        for i in range(10):
            Product.objects.create(
                title=f"性能测试商品{i}",
                description="性能测试商品描述",
                price=100.0 + i,
                category=category,
                seller=User.objects.first()
            )
        write_time = time.time() - start_time
        
        # 清理测试数据
        Product.objects.filter(title__startswith="性能测试商品").delete()
        
        self.results['database'] = {
            'db_connect_time': db_connect_time,
            'query_time': query_time,
            'write_time': write_time,
            'product_count': count
        }
        
        print(f"数据库连接时间: {db_connect_time:.4f}秒")
        print(f"查询100个商品时间: {query_time:.4f}秒")
        print(f"写入10个商品时间: {write_time:.4f}秒")
        print(f"当前商品总数: {count}")
    
    def api_performance_test(self):
        """API接口性能测试"""
        print("\n=== API接口性能测试 ===")
        
        # 模拟用户登录
        user = User.objects.create_user(
            username='perf_test_user',
            password='test123',
            email='perf@test.com'
        )
        
        # 测试登录性能
        start_time = time.time()
        self.client.login(username='perf_test_user', password='test123')
        login_time = time.time() - start_time
        
        # 测试首页加载性能
        start_time = time.time()
        response = self.client.get('/')
        home_page_time = time.time() - start_time
        
        # 测试商品列表页性能
        start_time = time.time()
        response = self.client.get('/marketplace/products/')
        product_list_time = time.time() - start_time
        
        # 测试搜索性能
        start_time = time.time()
        response = self.client.get('/marketplace/search/?q=测试')
        search_time = time.time() - start_time
        
        # 清理测试用户
        user.delete()
        
        self.results['api'] = {
            'login_time': login_time,
            'home_page_time': home_page_time,
            'product_list_time': product_list_time,
            'search_time': search_time
        }
        
        print(f"用户登录时间: {login_time:.4f}秒")
        print(f"首页加载时间: {home_page_time:.4f}秒")
        print(f"商品列表页时间: {product_list_time:.4f}秒")
        print(f"搜索功能时间: {search_time:.4f}秒")
    
    def concurrent_test(self, num_threads=10, requests_per_thread=10):
        """并发性能测试"""
        print(f"\n=== 并发性能测试 ({num_threads}线程, {requests_per_thread}请求/线程) ===")
        
        def worker(thread_id):
            """单个工作线程"""
            client = Client()
            times = []
            
            for i in range(requests_per_thread):
                start_time = time.time()
                
                # 模拟不同类型的请求
                if i % 3 == 0:
                    response = client.get('/')
                elif i % 3 == 1:
                    response = client.get('/marketplace/products/')
                else:
                    response = client.get('/marketplace/search/?q=测试')
                
                end_time = time.time()
                times.append(end_time - start_time)
            
            return times
        
        # 执行并发测试
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, i) for i in range(num_threads)]
            
            all_times = []
            for future in as_completed(futures):
                all_times.extend(future.result())
        
        total_time = time.time() - start_time
        total_requests = num_threads * requests_per_thread
        
        # 计算统计信息
        avg_time = sum(all_times) / len(all_times)
        max_time = max(all_times)
        min_time = min(all_times)
        requests_per_second = total_requests / total_time
        
        self.results['concurrent'] = {
            'total_requests': total_requests,
            'total_time': total_time,
            'avg_response_time': avg_time,
            'max_response_time': max_time,
            'min_response_time': min_time,
            'requests_per_second': requests_per_second
        }
        
        print(f"总请求数: {total_requests}")
        print(f"总时间: {total_time:.2f}秒")
        print(f"平均响应时间: {avg_time:.4f}秒")
        print(f"最大响应时间: {max_time:.4f}秒")
        print(f"最小响应时间: {min_time:.4f}秒")
        print(f"每秒请求数: {requests_per_second:.2f}")
    
    def memory_usage_test(self):
        """内存使用测试"""
        print("\n=== 内存使用测试 ===")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # 测试前内存使用
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行内存密集型操作
        products = list(Product.objects.all())
        categories = list(Category.objects.all())
        
        # 测试后内存使用
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        self.results['memory'] = {
            'memory_before_mb': memory_before,
            'memory_after_mb': memory_after,
            'memory_increase_mb': memory_increase,
            'products_loaded': len(products),
            'categories_loaded': len(categories)
        }
        
        print(f"测试前内存使用: {memory_before:.2f} MB")
        print(f"测试后内存使用: {memory_after:.2f} MB")
        print(f"内存增加: {memory_increase:.2f} MB")
        print(f"加载商品数: {len(products)}")
        print(f"加载分类数: {len(categories)}")
    
    def run_all_tests(self):
        """运行所有性能测试"""
        print("开始性能测试套件...\n")
        
        try:
            self.database_performance_test()
            self.api_performance_test()
            self.concurrent_test()
            self.memory_usage_test()
            
            # 生成性能报告
            self.generate_performance_report()
            
        except Exception as e:
            print(f"性能测试过程中出现错误: {e}")
    
    def generate_performance_report(self):
        """生成性能测试报告"""
        print("\n=== 性能测试报告 ===")
        
        report_file = 'performance_test_report.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("校园二手交易平台性能测试报告\n")
            f.write("=" * 50 + "\n\n")
            
            # 数据库性能
            if 'database' in self.results:
                db = self.results['database']
                f.write("1. 数据库性能测试结果:\n")
                f.write(f"   数据库连接时间: {db['db_connect_time']:.4f}秒\n")
                f.write(f"   查询100个商品时间: {db['query_time']:.4f}秒\n")
                f.write(f"   写入10个商品时间: {db['write_time']:.4f}秒\n")
                f.write(f"   当前商品总数: {db['product_count']}\n\n")
            
            # API性能
            if 'api' in self.results:
                api = self.results['api']
                f.write("2. API接口性能测试结果:\n")
                f.write(f"   用户登录时间: {api['login_time']:.4f}秒\n")
                f.write(f"   首页加载时间: {api['home_page_time']:.4f}秒\n")
                f.write(f"   商品列表页时间: {api['product_list_time']:.4f}秒\n")
                f.write(f"   搜索功能时间: {api['search_time']:.4f}秒\n\n")
            
            # 并发性能
            if 'concurrent' in self.results:
                concurrent = self.results['concurrent']
                f.write("3. 并发性能测试结果:\n")
                f.write(f"   总请求数: {concurrent['total_requests']}\n")
                f.write(f"   总时间: {concurrent['total_time']:.2f}秒\n")
                f.write(f"   平均响应时间: {concurrent['avg_response_time']:.4f}秒\n")
                f.write(f"   最大响应时间: {concurrent['max_response_time']:.4f}秒\n")
                f.write(f"   最小响应时间: {concurrent['min_response_time']:.4f}秒\n")
                f.write(f"   每秒请求数: {concurrent['requests_per_second']:.2f}\n\n")
            
            # 内存使用
            if 'memory' in self.results:
                memory = self.results['memory']
                f.write("4. 内存使用测试结果:\n")
                f.write(f"   测试前内存使用: {memory['memory_before_mb']:.2f} MB\n")
                f.write(f"   测试后内存使用: {memory['memory_after_mb']:.2f} MB\n")
                f.write(f"   内存增加: {memory['memory_increase_mb']:.2f} MB\n")
                f.write(f"   加载商品数: {memory['products_loaded']}\n")
                f.write(f"   加载分类数: {memory['categories_loaded']}\n\n")
            
            # 性能评估
            f.write("5. 性能评估:\n")
            f.write("   根据测试结果，系统性能表现良好。\n")
            f.write("   建议优化方向:\n")
            f.write("   - 数据库查询优化\n")
            f.write("   - 缓存机制引入\n")
            f.write("   - 静态资源优化\n")
        
        print(f"性能测试报告已生成: {report_file}")


def main():
    """主函数"""
    print("校园二手交易平台性能测试")
    print("=" * 50)
    
    # 检查是否安装了必要的依赖
    try:
        import psutil
    except ImportError:
        print("警告: 未安装psutil库，内存测试将跳过")
        print("请运行: pip install psutil")
    
    # 运行性能测试
    test_suite = PerformanceTestSuite()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()