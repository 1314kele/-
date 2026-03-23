#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
校园二手交易平台自动化测试运行器
一键运行所有测试并生成综合报告
"""

import os
import sys
import time
import subprocess
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')

import django
django.setup()

from test_config import get_test_config, check_environment


class AutomatedTestRunner:
    """自动化测试运行器"""
    
    def __init__(self):
        self.config = get_test_config()
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def check_prerequisites(self):
        """检查测试前提条件"""
        print("检查测试环境...")
        
        # 检查环境问题
        issues = check_environment()
        if issues:
            print("发现环境问题:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        
        # 检查依赖包
        required_packages = ['django', 'psutil', 'requests']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print("缺少依赖包:")
            for package in missing_packages:
                print(f"  - {package}")
            print("请运行: pip install " + " ".join(missing_packages))
            return False
        
        print("环境检查通过")
        return True
    
    def run_unit_tests(self):
        """运行单元测试"""
        print("\n=== 运行单元测试 ===")
        
        try:
            # 使用Django测试框架运行单元测试
            result = subprocess.run([
                sys.executable, 'manage.py', 'test', 'marketplace.tests',
                '--verbosity=2'
            ], capture_output=True, text=True, timeout=300)
            
            self.test_results['unit_tests'] = {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'returncode': result.returncode
            }
            
            if result.returncode == 0:
                print("✓ 单元测试通过")
            else:
                print("✗ 单元测试失败")
                print(result.stderr)
                
        except subprocess.TimeoutExpired:
            print("✗ 单元测试超时")
            self.test_results['unit_tests'] = {
                'success': False,
                'error': '测试超时'
            }
        except Exception as e:
            print(f"✗ 单元测试错误: {e}")
            self.test_results['unit_tests'] = {
                'success': False,
                'error': str(e)
            }
    
    def run_functional_tests(self):
        """运行功能测试"""
        print("\n=== 运行功能测试 ===")
        
        try:
            # 导入并运行功能测试
            from functional_test import FunctionalTestSuite
            
            # 重定向输出到文件
            import io
            from contextlib import redirect_stdout
            
            output_buffer = io.StringIO()
            
            with redirect_stdout(output_buffer):
                test_suite = FunctionalTestSuite()
                test_suite.run_all_functional_tests()
            
            self.test_results['functional_tests'] = {
                'success': test_suite.test_results['failed'] == 0,
                'passed': test_suite.test_results['passed'],
                'failed': test_suite.test_results['failed'],
                'errors': test_suite.test_results['errors'],
                'output': output_buffer.getvalue()
            }
            
            if test_suite.test_results['failed'] == 0:
                print("✓ 功能测试通过")
            else:
                print(f"✗ 功能测试失败: {test_suite.test_results['failed']}个测试失败")
                
        except Exception as e:
            print(f"✗ 功能测试错误: {e}")
            self.test_results['functional_tests'] = {
                'success': False,
                'error': str(e)
            }
    
    def run_performance_tests(self):
        """运行性能测试"""
        print("\n=== 运行性能测试 ===")
        
        try:
            # 导入并运行性能测试
            from performance_test import PerformanceTestSuite
            
            import io
            from contextlib import redirect_stdout
            
            output_buffer = io.StringIO()
            
            with redirect_stdout(output_buffer):
                test_suite = PerformanceTestSuite()
                test_suite.run_all_tests()
            
            self.test_results['performance_tests'] = {
                'success': True,  # 性能测试通常不设通过/失败标准
                'results': test_suite.results,
                'output': output_buffer.getvalue()
            }
            
            print("✓ 性能测试完成")
            
        except Exception as e:
            print(f"✗ 性能测试错误: {e}")
            self.test_results['performance_tests'] = {
                'success': False,
                'error': str(e)
            }
    
    def run_security_tests(self):
        """运行安全测试"""
        print("\n=== 运行安全测试 ===")
        
        try:
            # 运行安全相关的单元测试
            result = subprocess.run([
                sys.executable, 'manage.py', 'test', 
                'marketplace.tests.test_security.SecurityTest',
                '--verbosity=1'
            ], capture_output=True, text=True, timeout=120)
            
            self.test_results['security_tests'] = {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'returncode': result.returncode
            }
            
            if result.returncode == 0:
                print("✓ 安全测试通过")
            else:
                print("✗ 安全测试失败")
                
        except subprocess.TimeoutExpired:
            print("✗ 安全测试超时")
            self.test_results['security_tests'] = {
                'success': False,
                'error': '测试超时'
            }
        except Exception as e:
            print(f"✗ 安全测试错误: {e}")
            self.test_results['security_tests'] = {
                'success': False,
                'error': str(e)
            }
    
    def generate_comprehensive_report(self):
        """生成综合测试报告"""
        print("\n=== 生成测试报告 ===")
        
        # 计算测试时间
        test_duration = self.end_time - self.start_time
        
        # 统计测试结果
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for test_type, result in self.test_results.items():
            if 'passed' in result and 'failed' in result:
                total_tests += result['passed'] + result['failed']
                passed_tests += result['passed']
                failed_tests += result['failed']
            elif 'success' in result:
                total_tests += 1
                if result['success']:
                    passed_tests += 1
                else:
                    failed_tests += 1
        
        # 生成HTML报告
        self.generate_html_report(test_duration, total_tests, passed_tests, failed_tests)
        
        # 生成JSON报告
        self.generate_json_report(test_duration)
        
        print("✓ 测试报告生成完成")
    
    def generate_html_report(self, duration, total, passed, failed):
        """生成HTML格式的测试报告"""
        report_file = 'comprehensive_test_report.html'
        
        # 计算通过率
        success_rate = (passed / total * 100) if total > 0 else 0
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>校园二手交易平台测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .test-result {{ margin: 10px 0; padding: 10px; border-left: 4px solid; }}
        .passed {{ border-color: #28a745; background: #f8fff9; }}
        .failed {{ border-color: #dc3545; background: #fff5f5; }}
        .progress-bar {{ background: #e9ecef; height: 20px; border-radius: 10px; overflow: hidden; }}
        .progress {{ background: #28a745; height: 100%; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>校园二手交易平台测试报告</h1>
        <p>测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>测试持续时间: {duration:.2f}秒</p>
    </div>
    
    <div class="summary">
        <h2>测试摘要</h2>
        <p>总测试数: {total}</p>
        <p>通过测试: {passed}</p>
        <p>失败测试: {failed}</p>
        <p>通过率: {success_rate:.1f}%</p>
        
        <div class="progress-bar">
            <div class="progress" style="width: {success_rate}%"></div>
        </div>
    </div>
    
    <div class="detailed-results">
        <h2>详细测试结果</h2>
        """
        
        # 添加各个测试类型的结果
        for test_type, result in self.test_results.items():
            status_class = "passed" if result.get('success', False) else "failed"
            status_text = "通过" if result.get('success', False) else "失败"
            
            html_content += f"""
        <div class="test-result {status_class}">
            <h3>{test_type.replace('_', ' ').title()} - {status_text}</h3>
            """
            
            if 'passed' in result and 'failed' in result:
                html_content += f"<p>通过: {result['passed']}, 失败: {result['failed']}</p>"
            
            if 'error' in result:
                html_content += f"<p>错误: {result['error']}</p>"
            
            html_content += "</div>"
        
        html_content += """
    </div>
    
    <div class="recommendations">
        <h2>改进建议</h2>
        <ul>
            <li>定期运行自动化测试</li>
            <li>关注失败测试并及时修复</li>
            <li>优化性能测试结果中的瓶颈</li>
            <li>加强安全测试覆盖</li>
        </ul>
    </div>
</body>
</html>
        """
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML报告已生成: {report_file}")
    
    def generate_json_report(self, duration):
        """生成JSON格式的测试报告"""
        report_file = 'test_results.json'
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'test_results': self.test_results,
            'summary': {
                'total_tests': sum([
                    r.get('passed', 0) + r.get('failed', 0) 
                    for r in self.test_results.values() 
                    if isinstance(r, dict)
                ]),
                'passed_tests': sum([
                    r.get('passed', 1 if r.get('success', False) else 0)
                    for r in self.test_results.values() 
                    if isinstance(r, dict)
                ]),
                'failed_tests': sum([
                    r.get('failed', 0 if r.get('success', False) else 1)
                    for r in self.test_results.values() 
                    if isinstance(r, dict)
                ])
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"JSON报告已生成: {report_file}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始自动化测试...")
        print("=" * 60)
        
        # 记录开始时间
        self.start_time = time.time()
        
        # 检查前提条件
        if not self.check_prerequisites():
            print("测试前提条件不满足，停止测试")
            return
        
        # 运行各种测试
        self.run_unit_tests()
        self.run_functional_tests()
        self.run_performance_tests()
        self.run_security_tests()
        
        # 记录结束时间
        self.end_time = time.time()
        
        # 生成报告
        self.generate_comprehensive_report()
        
        print("\n" + "=" * 60)
        print("自动化测试完成")
        
        # 显示测试结果摘要
        total_failed = sum([
            0 if r.get('success', True) else 1 
            for r in self.test_results.values()
        ])
        
        if total_failed == 0:
            print("🎉 所有测试通过！")
        else:
            print(f"⚠️  {total_failed}个测试类型失败，请查看详细报告")


def main():
    """主函数"""
    print("校园二手交易平台自动化测试运行器")
    print("=" * 50)
    
    runner = AutomatedTestRunner()
    runner.run_all_tests()


if __name__ == "__main__":
    main()