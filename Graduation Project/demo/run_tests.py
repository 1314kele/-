#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园二手交易平台测试运行脚本
专门用于性能测试和功能测试
"""

import os
import sys
import time
import subprocess
import json
from datetime import datetime
from pathlib import Path

def setup_test_environment():
    """设置测试环境"""
    print("🔧 设置测试环境...")
    
    # 检查当前目录
    current_dir = Path(__file__).parent
    print(f"当前工作目录: {current_dir}")
    
    # 检查虚拟环境
    venv_path = current_dir / ".venv"
    if venv_path.exists():
        print("✅ 虚拟环境存在")
    else:
        print("⚠️  虚拟环境不存在，将使用系统Python")
    
    # 检查数据库文件
    db_path = current_dir / "db.sqlite3"
    if db_path.exists():
        print("✅ 数据库文件存在")
    else:
        print("⚠️  数据库文件不存在，将尝试创建测试数据库")
        try:
            subprocess.run([
                sys.executable, "manage.py", "migrate"
            ], cwd=current_dir, check=True, capture_output=True)
            print("✅ 测试数据库创建成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ 数据库创建失败: {e}")
    
    print("✅ 环境设置完成")

def run_functional_test():
    """运行功能测试"""
    print("\n🔧 开始功能测试...")
    
    start_time = time.time()
    
    try:
        # 运行功能测试脚本
        result = subprocess.run([
            sys.executable, "functional_test.py"
        ], capture_output=True, text=True, timeout=300)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 解析输出结果
        output_lines = result.stdout.split('\n')
        passed_tests = 0
        failed_tests = 0
        
        for line in output_lines:
            if "测试通过" in line or "✓" in line:
                passed_tests += 1
            elif "测试失败" in line or "✗" in line:
                failed_tests += 1
        
        if result.returncode == 0 and failed_tests == 0:
            print("✅ 功能测试通过")
            return {
                "status": "passed",
                "execution_time": execution_time,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "output": result.stdout[-500:],  # 只保留最后500字符
                "errors": result.stderr
            }
        else:
            print("❌ 功能测试失败")
            return {
                "status": "failed",
                "execution_time": execution_time,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "output": result.stdout[-500:],
                "errors": result.stderr
            }
            
    except subprocess.TimeoutExpired:
        print("❌ 功能测试超时")
        return {
            "status": "timeout",
            "execution_time": 300,
            "passed_tests": 0,
            "failed_tests": 0,
            "output": "测试执行超时（5分钟）",
            "errors": "Timeout"
        }
    except Exception as e:
        print(f"❌ 功能测试执行异常: {e}")
        return {
            "status": "error",
            "execution_time": time.time() - start_time,
            "passed_tests": 0,
            "failed_tests": 0,
            "output": "",
            "errors": str(e)
        }

def run_performance_test():
    """运行性能测试"""
    print("\n⚡ 开始性能测试...")
    
    start_time = time.time()
    
    try:
        # 运行性能测试脚本
        result = subprocess.run([
            sys.executable, "performance_test.py"
        ], capture_output=True, text=True, timeout=600)  # 10分钟超时
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 提取性能指标
        metrics = extract_performance_metrics(result.stdout)
        
        if result.returncode == 0:
            print("✅ 性能测试完成")
            return {
                "status": "completed",
                "execution_time": execution_time,
                "output": result.stdout[-500:],
                "errors": result.stderr,
                "metrics": metrics
            }
        else:
            print("❌ 性能测试失败")
            return {
                "status": "failed",
                "execution_time": execution_time,
                "output": result.stdout[-500:],
                "errors": result.stderr,
                "metrics": metrics
            }
            
    except subprocess.TimeoutExpired:
        print("❌ 性能测试超时")
        return {
            "status": "timeout",
            "execution_time": 600,
            "output": "测试执行超时（10分钟）",
            "errors": "Timeout",
            "metrics": {}
        }
    except Exception as e:
        print(f"❌ 性能测试执行异常: {e}")
        return {
            "status": "error",
            "execution_time": time.time() - start_time,
            "output": "",
            "errors": str(e),
            "metrics": {}
        }

def extract_performance_metrics(output):
    """从性能测试输出中提取指标"""
    metrics = {}
    
    lines = output.split('\n')
    for line in lines:
        if "平均响应时间" in line:
            try:
                metrics["avg_response_time"] = float(line.split(":")[1].strip().split(" ")[0])
            except:
                pass
        elif "每秒请求数" in line:
            try:
                metrics["requests_per_second"] = float(line.split(":")[1].strip().split(" ")[0])
            except:
                pass
        elif "数据库连接时间" in line:
            try:
                metrics["db_connection_time"] = float(line.split(":")[1].strip().split(" ")[0])
            except:
                pass
        elif "内存使用增加" in line:
            try:
                metrics["memory_increase"] = float(line.split(":")[1].strip().split(" ")[0])
            except:
                pass
        elif "并发测试完成" in line:
            try:
                parts = line.split("-")
                if len(parts) > 1:
                    metrics["concurrent_requests"] = int(parts[1].split("个")[0].strip())
            except:
                pass
    
    return metrics

def generate_simple_report(test_results):
    """生成简单的测试报告"""
    print("\n📊 生成测试报告...")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 生成文本报告
    report_content = f"""
校园二手交易平台测试报告
==========================

测试时间: {timestamp}
总执行时间: {test_results['total_execution_time']:.2f} 秒

功能测试结果:
------------
状态: {test_results['functional_test']['status']}
执行时间: {test_results['functional_test']['execution_time']:.2f} 秒
通过测试: {test_results['functional_test'].get('passed_tests', 0)}
失败测试: {test_results['functional_test'].get('failed_tests', 0)}

性能测试结果:
------------
状态: {test_results['performance_test']['status']}
执行时间: {test_results['performance_test']['execution_time']:.2f} 秒

性能指标:
"""
    
    # 添加性能指标
    metrics = test_results['performance_test'].get('metrics', {})
    for metric_name, metric_value in metrics.items():
        report_content += f"{metric_name}: {metric_value}\n"
    
    # 添加测试建议
    report_content += f"""
测试建议:
--------
"""
    
    recommendations = generate_recommendations(test_results)
    for rec in recommendations:
        report_content += f"- {rec}\n"
    
    # 保存文本报告
    report_path = Path(__file__).parent / "simple_test_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ 文本报告已生成: {report_path}")
    
    # 生成JSON报告
    json_report = {
        "timestamp": timestamp,
        "total_execution_time": test_results['total_execution_time'],
        "functional_test": test_results['functional_test'],
        "performance_test": test_results['performance_test'],
        "recommendations": recommendations
    }
    
    json_path = Path(__file__).parent / "simple_test_results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON报告已生成: {json_path}")
    
    return report_path, json_path

def generate_recommendations(test_results):
    """生成测试建议"""
    recommendations = []
    
    # 功能测试建议
    functional_test = test_results['functional_test']
    if functional_test['status'] != 'passed':
        recommendations.append("修复功能测试中的失败用例")
    
    # 性能测试建议
    performance_test = test_results['performance_test']
    metrics = performance_test.get('metrics', {})
    
    if metrics:
        if metrics.get('avg_response_time', 0) > 1.0:
            recommendations.append("优化API响应时间，目标应小于1秒")
        if metrics.get('requests_per_second', 0) < 20:
            recommendations.append("提升系统并发处理能力")
        if metrics.get('db_connection_time', 0) > 0.1:
            recommendations.append("优化数据库连接性能")
        if metrics.get('memory_increase', 0) > 50:
            recommendations.append("优化内存使用，减少内存泄漏")
    
    if performance_test['status'] != 'completed':
        recommendations.append("检查性能测试执行环境")
    
    if not recommendations:
        recommendations.append("所有测试通过，系统运行良好")
    
    return recommendations

def main():
    """主函数"""
    print("🚀 校园二手交易平台测试运行器")
    print("=" * 60)
    print("📋 测试内容: 功能测试 + 性能测试")
    print("=" * 60)
    
    start_time = time.time()
    
    # 设置环境
    setup_test_environment()
    
    # 运行测试
    test_results = {
        'functional_test': run_functional_test(),
        'performance_test': run_performance_test(),
        'total_execution_time': 0
    }
    
    # 计算总执行时间
    total_time = time.time() - start_time
    test_results['total_execution_time'] = total_time
    
    # 生成报告
    text_report, json_report = generate_simple_report(test_results)
    
    # 显示测试摘要
    print("\n" + "=" * 60)
    print("📋 测试摘要")
    print("=" * 60)
    print(f"总执行时间: {total_time:.2f} 秒")
    print(f"功能测试: {test_results['functional_test']['status']}")
    print(f"性能测试: {test_results['performance_test']['status']}")
    
    # 显示性能指标
    metrics = test_results['performance_test'].get('metrics', {})
    if metrics:
        print("\n📈 性能指标:")
        for metric_name, metric_value in metrics.items():
            print(f"  {metric_name}: {metric_value}")
    
    print(f"\n📊 报告文件:")
    print(f"  - 文本报告: {text_report}")
    print(f"  - JSON报告: {json_report}")
    
    print("\n🎯 建议:")
    recommendations = generate_recommendations(test_results)
    for rec in recommendations:
        print(f"  • {rec}")
    
    print("\n✅ 测试完成!")
    print("💡 提示: 查看详细报告了解具体测试结果")

if __name__ == "__main__":
    main()