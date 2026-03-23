"""
校园二手交易平台 - 功能模块E-R图生成脚本
生成详细的实体关系图
"""

import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import matplotlib.font_manager as fm
import numpy as np

def setup_chinese_font():
    """设置中文字体支持"""
    chinese_fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 'FangSong']
    
    for font_name in chinese_fonts:
        try:
            plt.rcParams['font.sans-serif'] = [font_name, 'Arial']
            plt.rcParams['axes.unicode_minus'] = False
            print(f"✅ 使用字体: {font_name}")
            return True
        except:
            continue
    
    print("⚠️ 未找到合适的中文字体，将使用默认字体")
    return False

def create_er_diagram():
    """创建功能模块E-R图"""
    
    setup_chinese_font()
    
    # 创建更大的图形以容纳所有实体
    fig, ax = plt.subplots(1, 1, figsize=(20, 16))
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 16)
    ax.axis('off')
    
    # 颜色方案 - 按功能模块分组
    colors = {
        'user': '#4A90E2',        # 蓝色 - 用户相关
        'product': '#7ED321',     # 绿色 - 商品相关
        'transaction': '#BD10E0', # 紫色 - 交易相关
        'security': '#F5A623',    # 橙色 - 安全相关
        'analysis': '#417505',    # 深绿 - 分析相关
        'recommendation': '#D0021B', # 红色 - 推荐相关
        'knowledge': '#8B572A',   # 棕色 - 知识相关
        'system': '#4A4A4A'      # 灰色 - 系统相关
    }
    
    # 1. 核心实体 - 用户和商品（中心位置）
    core_entities = [
        (9, 12, '👤 User\n用户表', colors['user'], [
            'username (用户名)',
            'email (邮箱)',
            'password (密码)',
            'date_joined (注册时间)'
        ]),
        (9, 8, '📦 Product\n商品表', colors['product'], [
            'title (标题)',
            'description (描述)',
            'price (价格)',
            'seller (卖家)',
            'category (分类)',
            'status (状态)'
        ])
    ]
    
    # 2. 商品管理模块实体（左侧）
    product_entities = [
        (3, 10, '📁 Category\n商品分类', colors['product'], [
            'name (分类名)',
            'description (描述)'
        ]),
        (3, 8, '❤️ Favorite\n收藏夹', colors['product'], [
            'user (用户)',
            'product (商品)',
            'created_at (收藏时间)'
        ]),
        (3, 6, '⭐ Review\n用户评价', colors['product'], [
            'reviewer (评价者)',
            'reviewed_user (被评价者)',
            'rating (评分)',
            'comment (评价内容)'
        ])
    ]
    
    # 3. 交易管理模块实体（右侧）
    transaction_entities = [
        (15, 10, '💳 Transaction\n交易记录', colors['transaction'], [
            'buyer (买家)',
            'seller (卖家)',
            'product (商品)',
            'price (价格)',
            'status (状态)'
        ]),
        (15, 8, '💬 Message\n用户消息', colors['transaction'], [
            'sender (发送者)',
            'receiver (接收者)',
            'content (内容)',
            'is_read (已读状态)'
        ])
    ]
    
    # 4. 安全与推荐模块实体（底部左侧）
    security_entities = [
        (3, 4, '🔐 TwoFactorAuth\n双因素认证', colors['security'], [
            'user (用户)',
            'is_enabled (是否启用)',
            'secret_key (密钥)'
        ]),
        (3, 2, '📊 SecurityLog\n安全日志', colors['security'], [
            'user (用户)',
            'log_type (日志类型)',
            'ip_address (IP地址)'
        ]),
        (6, 4, '🤖 RecommendationLog\n推荐日志', colors['recommendation'], [
            'user (用户)',
            'product (商品)',
            'recommendation_type (推荐类型)',
            'score (推荐分数)'
        ]),
        (6, 2, '📈 UserPreference\n用户偏好', colors['recommendation'], [
            'user (用户)',
            'category (分类)',
            'preference_score (偏好分数)'
        ])
    ]
    
    # 5. 分析与知识模块实体（底部右侧）
    analysis_entities = [
        (12, 4, '📊 UserBehavior\n用户行为', colors['analysis'], [
            'user (用户)',
            'action_type (行为类型)',
            'action_time (行为时间)',
            'ip_address (IP地址)'
        ]),
        (12, 2, '⚠️ AbnormalBehavior\n异常行为', colors['analysis'], [
            'user (用户)',
            'abnormal_type (异常类型)',
            'risk_score (风险分值)'
        ]),
        (15, 4, '📚 Knowledge\n知识库', colors['knowledge'], [
            'knowledge_type (知识类型)',
            'title (标题)',
            'content (内容)',
            'keywords (关键词)'
        ]),
        (15, 2, '⚙️ BehaviorConfig\n系统配置', colors['system'], [
            'config_key (配置键)',
            'config_value (配置值)',
            'description (描述)'
        ])
    ]
    
    # 绘制所有实体
    all_entities = core_entities + product_entities + transaction_entities + security_entities + analysis_entities
    
    for x, y, title, color, attributes in all_entities:
        # 计算实体框大小
        attr_count = len(attributes)
        height = 0.8 + attr_count * 0.15
        
        # 绘制实体框
        box = FancyBboxPatch((x - 1.5, y - height/2), 3, height, 
                            boxstyle="round,pad=0.2", 
                            facecolor=color, alpha=0.9, 
                            edgecolor='white', linewidth=2)
        ax.add_patch(box)
        
        # 实体标题
        ax.text(x, y + height/2 - 0.15, title, ha='center', va='center', 
                fontsize=10, fontweight='bold', color='white')
        
        # 实体属性
        for i, attr in enumerate(attributes):
            attr_y = y + height/2 - 0.4 - i * 0.15
            ax.text(x, attr_y, attr, ha='center', va='center', 
                    fontsize=7, color='white')
    
    # 绘制关系连接线
    relationships = [
        # 用户相关关系
        ((9, 11.4), (9, 10.6)),  # User -> Product (一对多)
        ((9, 11.4), (3, 10.6)),  # User -> Category (一对多)
        ((9, 11.4), (3, 8.6)),   # User -> Favorite (一对多)
        ((9, 11.4), (3, 6.6)),   # User -> Review (一对多)
        ((9, 11.4), (15, 10.6)), # User -> Transaction (一对多)
        ((9, 11.4), (15, 8.6)),  # User -> Message (一对多)
        ((9, 11.4), (3, 4.6)),   # User -> TwoFactorAuth (一对一)
        ((9, 11.4), (3, 2.6)),   # User -> SecurityLog (一对多)
        ((9, 11.4), (6, 4.6)),   # User -> RecommendationLog (一对多)
        ((9, 11.4), (6, 2.6)),   # User -> UserPreference (一对多)
        ((9, 11.4), (12, 4.6)),  # User -> UserBehavior (一对多)
        ((9, 11.4), (12, 2.6)),  # User -> AbnormalBehavior (一对多)
        
        # 商品相关关系
        ((9, 7.4), (3, 9.4)),    # Product -> Category (多对一)
        ((9, 7.4), (3, 7.4)),    # Product -> Favorite (一对多)
        ((9, 7.4), (3, 5.4)),    # Product -> Review (一对多)
        ((9, 7.4), (15, 9.4)),   # Product -> Transaction (一对多)
        ((9, 7.4), (15, 7.4)),   # Product -> Message (一对多)
        ((9, 7.4), (6, 3.4)),    # Product -> RecommendationLog (一对多)
        
        # 推荐系统关系
        ((6, 3.4), (3, 9.4)),    # UserPreference -> Category (多对一)
        
        # 行为分析关系
        ((12, 3.4), (12, 1.4)),  # UserBehavior -> AbnormalBehavior (一对多)
    ]
    
    for (x1, y1), (x2, y2) in relationships:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1), 
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='#666666', 
                                   shrinkA=8, shrinkB=8, alpha=0.7))
    
    # 添加关系说明
    relationship_notes = [
        (1, 15.5, '🔗 关系说明:', '#2c3e50'),
        (1, 15.0, '• 实线箭头: 一对多关系', '#2c3e50'),
        (1, 14.5, '• 虚线箭头: 一对一关系', '#2c3e50'),
        (1, 14.0, '• 颜色分组: 按功能模块分类', '#2c3e50'),
    ]
    
    for x, y, text, color in relationship_notes:
        ax.text(x, y, text, ha='left', va='center', fontsize=10, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#f8f9fa', 
                         alpha=0.9, edgecolor='#dee2e6', linewidth=1))
    
    # 添加功能模块分组说明
    module_groups = [
        (2, 13, '📦 商品管理模块', colors['product']),
        (8, 13, '👤 用户核心模块', colors['user']),
        (14, 13, '💳 交易管理模块', colors['transaction']),
        (2, 1, '🔐 安全与推荐模块', colors['security']),
        (8, 1, '📊 行为分析模块', colors['analysis']),
        (14, 1, '📚 知识与系统模块', colors['knowledge'])
    ]
    
    for x, y, text, color in module_groups:
        ax.text(x, y, text, ha='center', va='center', fontsize=11, 
                fontweight='bold', bbox=dict(boxstyle="round,pad=0.4", 
                facecolor=color, alpha=0.8, edgecolor='white', linewidth=2))
    
    # 设置标题
    plt.title('🏫 校园二手交易平台 - 功能模块E-R图\nEntity-Relationship Diagram', 
              fontsize=18, fontweight='bold', pad=25, color='#2c3e50')
    
    # 添加水印信息
    ax.text(17.8, 0.2, 'E-R图 v1.0', ha='right', va='bottom', 
            fontsize=8, color='#95a5a6', alpha=0.5)
    
    # 调整布局并保存
    plt.tight_layout()
    plt.savefig('D:\\Graduation Project\\demo\\er_diagram.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    
    print("✅ E-R图已生成:")
    print("- er_diagram.png (高分辨率PNG)")
    plt.close()

def create_simple_er_diagram():
    """创建简化版E-R图（更清晰的布局）"""
    
    setup_chinese_font()
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # 颜色方案
    colors = {
        'user': '#4A90E2',
        'product': '#7ED321',
        'transaction': '#BD10E0',
        'security': '#F5A623',
        'analysis': '#417505',
        'recommendation': '#D0021B'
    }
    
    # 核心实体（简化布局）
    entities = [
        (7, 9, '👤 User\n用户', colors['user']),
        (3, 7, '📦 Product\n商品', colors['product']),
        (11, 7, '💳 Transaction\n交易', colors['transaction']),
        (3, 5, '📊 Category\n分类', colors['product']),
        (7, 5, '🔐 Security\n安全', colors['security']),
        (11, 5, '📈 Analysis\n分析', colors['analysis']),
        (7, 3, '🤖 Recommendation\n推荐', colors['recommendation'])
    ]
    
    # 绘制实体（圆形）
    for x, y, label, color in entities:
        circle = plt.Circle((x, y), 0.8, color=color, alpha=0.9, 
                          edgecolor='white', linewidth=2)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white')
    
    # 绘制关系连接线
    relationships = [
        ((7, 8.2), (3, 7.8)),    # User -> Product
        ((7, 8.2), (11, 7.8)),   # User -> Transaction
        ((3, 6.2), (7, 5.8)),    # Product -> Security
        ((11, 6.2), (7, 5.8)),   # Transaction -> Security
        ((3, 5.8), (7, 4.2)),    # Category -> Recommendation
        ((7, 4.2), (11, 5.8)),   # Recommendation -> Analysis
        ((7, 5.8), (7, 4.2)),    # Security -> Recommendation
    ]
    
    for (x1, y1), (x2, y2) in relationships:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1), 
                    arrowprops=dict(arrowstyle='->', lw=2, color='#3498db', 
                                   shrinkA=8, shrinkB=8, alpha=0.8))
    
    plt.title('🏫 校园二手交易平台 - 简化E-R图\nSimplified ER Diagram', 
              fontsize=16, fontweight='bold', pad=20, color='#2c3e50')
    
    plt.tight_layout()
    plt.savefig('D:\\Graduation Project\\demo\\simple_er_diagram.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    
    print("✅ 简化E-R图已生成:")
    print("- simple_er_diagram.png")
    plt.close()

def create_er_documentation():
    """创建E-R图说明文档"""
    
    documentation = """
===================================================
            🏫 校园二手交易平台 - E-R图说明文档
===================================================

📋 实体关系图概述
-----------------

本E-R图展示了校园二手交易平台的数据库实体关系结构，
包含8个主要功能模块的实体和它们之间的关系。

🏗️ 核心实体结构
---------------

1. 👤 用户核心模块 (蓝色)
   - User: 系统用户表，包含用户基本信息
   - 关联实体: Product, Category, Favorite, Review, Transaction, Message等

2. 📦 商品管理模块 (绿色)
   - Product: 二手商品信息表
   - Category: 商品分类表
   - Favorite: 用户收藏夹
   - Review: 用户评价系统

3. 💳 交易管理模块 (紫色)
   - Transaction: 交易记录表
   - Message: 用户间消息系统

4. 🔐 安全与推荐模块 (橙色)
   - TwoFactorAuth: 双因素认证
   - SecurityLog: 安全日志记录
   - RecommendationLog: 推荐系统日志
   - UserPreference: 用户偏好设置

5. 📊 行为分析模块 (深绿色)
   - UserBehavior: 用户行为数据
   - AbnormalBehavior: 异常行为检测

6. 📚 知识与系统模块 (棕色/灰色)
   - Knowledge: 知识库系统
   - BehaviorConfig: 系统配置表

🔗 主要关系说明
---------------

1. 一对多关系 (实线箭头)
   - User → Product: 一个用户可以发布多个商品
   - User → Transaction: 一个用户可以参与多个交易
   - Product → Review: 一个商品可以有多个评价
   - User → UserBehavior: 一个用户可以有多个行为记录

2. 一对一关系 (虚线箭头)
   - User → TwoFactorAuth: 一个用户对应一个双因素认证设置

3. 多对一关系
   - Product → Category: 多个商品属于一个分类
   - UserPreference → Category: 多个用户偏好对应一个分类

🎨 设计特点
-----------

1. 颜色编码
   - 按功能模块进行颜色分组
   - 便于识别不同模块的实体

2. 布局优化
   - 核心实体位于中心位置
   - 相关模块实体围绕核心实体分布
   - 避免连接线交叉，提高可读性

3. 信息层次
   - 实体名称和主要属性清晰显示
   - 关系箭头明确标识方向
   - 分组说明便于理解模块结构

🔧 技术实现
-----------

1. 数据库设计
   - 基于Django ORM的模型设计
   - 支持SQLite3数据库
   - 包含完整的外键约束

2. 关系完整性
   - 级联删除保护数据完整性
   - 唯一约束确保数据一致性
   - 索引优化提高查询性能

📊 生成的文件
-------------

1. er_diagram.png
   - 详细功能模块E-R图
   - 包含所有实体和关系
   - 高分辨率300 DPI

2. simple_er_diagram.png
   - 简化版E-R图
   - 核心实体和主要关系
   - 更清晰的视觉层次

3. 本说明文档
   - 详细的技术说明
   - 实体关系解释
   - 设计理念说明

===================================================
生成时间: 2025年
版本: v1.0
===================================================
"""
    
    # 保存说明文档
    with open('D:\\Graduation Project\\demo\\er_documentation.txt', 'w', encoding='utf-8') as f:
        f.write(documentation)
    
    print("✅ E-R图说明文档已生成:")
    print("- er_documentation.txt")
    print(documentation)

if __name__ == "__main__":
    try:
        print("🚀 开始生成功能模块E-R图...")
        print("=" * 60)
        print("📋 生成内容:")
        print("1. 详细功能模块E-R图")
        print("2. 简化版E-R图")
        print("3. E-R图说明文档")
        print("=" * 60)
        
        # 生成详细E-R图
        create_er_diagram()
        
        # 生成简化E-R图
        create_simple_er_diagram()
        
        # 生成说明文档
        create_er_documentation()
        
        print("=" * 60)
        print("🎉 E-R图生成完成!")
        print("📁 文件保存在: D:\\Graduation Project\\demo\\")
        print("\n📋 生成的文件:")
        print("- er_diagram.png (详细E-R图)")
        print("- simple_er_diagram.png (简化E-R图)")
        print("- er_documentation.txt (说明文档)")
        
    except Exception as e:
        print(f"❌ 生成过程中出现错误: {e}")
        print("正在生成说明文档作为备用...")
        create_er_documentation()