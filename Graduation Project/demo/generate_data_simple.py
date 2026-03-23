"""
校园二手交易平台数据生成脚本（简化版）
生成真实的商品、用户、交易等数据，使用本地生成的占位图
"""

import os
import random
from datetime import datetime, timedelta
from django.utils import timezone
import json
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')
django.setup()

from marketplace.models import (
    Category, Product, User, Favorite, Message, Review, 
    Transaction, UserBehavior, AbnormalBehavior, BehaviorConfig,
    Warning as WarningModel, BehaviorReport, SystemLog,
    Knowledge, UserPreference, RecommendationLog, ProductSimilarity,
    TwoFactorAuth, SecurityLog, EncryptedData
)
from PIL import Image, ImageDraw, ImageFont

# 商品分类数据
CATEGORIES = [
    {
        'name': '电子设备',
        'description': '手机、电脑、平板等电子设备',
        'color': (102, 126, 234),  # 蓝色
        'products': [
            {'title': 'iPhone 13 128GB', 'price': 4500, 'condition': 'good', 'description': '个人使用，无维修史，功能完好，配原装充电器'},
            {'title': 'MacBook Pro 2020', 'price': 6800, 'condition': 'good', 'description': 'M1芯片，16GB内存，512GB存储，轻度使用'},
            {'title': 'iPad Air 4', 'price': 3200, 'condition': 'like_new', 'description': '几乎全新，只使用过几次，带保护套'},
            {'title': '小米11 Pro', 'price': 2800, 'condition': 'good', 'description': '8GB+256GB，无划痕，功能正常'},
            {'title': '华为Mate40', 'price': 3500, 'condition': 'fair', 'description': '使用一年，有轻微使用痕迹'},
            {'title': 'ThinkPad X1', 'price': 4200, 'condition': 'good', 'description': '商务本，性能强劲，适合办公学习'},
            {'title': 'AirPods Pro', 'price': 900, 'condition': 'like_new', 'description': '几乎全新，音质完美，降噪效果好'},
            {'title': 'Sony WH-1000XM4', 'price': 1500, 'condition': 'good', 'description': '降噪耳机，音质出色，续航持久'},
            {'title': 'Kindle Paperwhite', 'price': 800, 'condition': 'good', 'description': '电子书阅读器，护眼屏幕，适合阅读'},
            {'title': 'GoPro Hero9', 'price': 2200, 'condition': 'good', 'description': '运动相机，4K录制，防水设计'},
        ]
    },
    {
        'name': '书籍资料',
        'description': '教材、小说、参考书等',
        'color': (52, 152, 219),  # 绿色
        'products': [
            {'title': '高等数学同济第七版', 'price': 25, 'condition': 'good', 'description': '大学教材，有少量笔记，整体完好'},
            {'title': '英语四级词汇书', 'price': 15, 'condition': 'like_new', 'description': '全新未使用，词汇详解，附音频'},
            {'title': 'Python编程从入门到实践', 'price': 45, 'condition': 'good', 'description': '编程入门书籍，有少量标记'},
            {'title': '三体全集', 'price': 60, 'condition': 'good', 'description': '科幻小说三部曲，品相完好'},
            {'title': '考研英语真题', 'price': 35, 'condition': 'fair', 'description': '历年真题，有解题痕迹'},
            {'title': '计算机网络谢希仁', 'price': 30, 'condition': 'good', 'description': '经典教材，内容详实'},
            {'title': '数据结构与算法', 'price': 40, 'condition': 'good', 'description': '计算机专业教材，重点突出'},
            {'title': '百年孤独', 'price': 28, 'condition': 'like_new', 'description': '经典文学作品，几乎全新'},
            {'title': 'JavaScript高级程序设计', 'price': 55, 'condition': 'good', 'description': '前端开发必备，内容全面'},
            {'title': '机器学习实战', 'price': 65, 'condition': 'good', 'description': 'AI入门书籍，案例丰富'},
        ]
    },
    {
        'name': '生活用品',
        'description': '日用品、家具、装饰等',
        'color': (241, 196, 15),  # 橙色
        'products': [
            {'title': '宜家台灯', 'price': 80, 'condition': 'good', 'description': 'LED台灯，护眼设计，亮度可调'},
            {'title': '折叠椅', 'price': 45, 'condition': 'good', 'description': '便携折叠椅，适合宿舍使用'},
            {'title': '电热水壶', 'price': 35, 'condition': 'good', 'description': '1.5L容量，快速烧水，安全可靠'},
            {'title': '小风扇', 'price': 25, 'condition': 'fair', 'description': 'USB供电，静音设计，夏天必备'},
            {'title': '收纳盒套装', 'price': 30, 'condition': 'like_new', 'description': '多功能收纳，节省空间'},
            {'title': '瑜伽垫', 'price': 40, 'condition': 'good', 'description': '防滑瑜伽垫，厚度适中，环保材质'},
            {'title': '加湿器', 'price': 55, 'condition': 'good', 'description': '静音加湿，大容量水箱，适合干燥天气'},
            {'title': '台式小冰箱', 'price': 200, 'condition': 'good', 'description': '迷你冰箱，适合宿舍使用，制冷效果好'},
            {'title': '床上用品四件套', 'price': 120, 'condition': 'good', 'description': '纯棉材质，舒适透气，图案精美'},
            {'title': '挂烫机', 'price': 85, 'condition': 'good', 'description': '手持挂烫机，快速除皱，便携设计'},
        ]
    },
    {
        'name': '运动器材',
        'description': '健身器材、运动装备等',
        'color': (231, 76, 60),  # 红色
        'products': [
            {'title': '瑜伽球', 'price': 35, 'condition': 'good', 'description': '抗爆瑜伽球，适合健身塑形'},
            {'title': '哑铃套装', 'price': 80, 'condition': 'good', 'description': '可调节重量，包含多种规格'},
            {'title': '跳绳', 'price': 15, 'condition': 'like_new', 'description': '计数跳绳，材质耐用，适合有氧运动'},
            {'title': '跑步机', 'price': 800, 'condition': 'fair', 'description': '家用跑步机，多功能显示，可折叠'},
            {'title': '羽毛球拍', 'price': 45, 'condition': 'good', 'description': '专业羽毛球拍，手感舒适，耐用性强'},
            {'title': '篮球', 'price': 25, 'condition': 'good', 'description': '标准篮球，材质优良，适合室外使用'},
            {'title': '健身垫', 'price': 50, 'condition': 'good', 'description': '加厚健身垫，防滑减震，保护关节'},
            {'title': '拉力器', 'price': 30, 'condition': 'good', 'description': '家用拉力器，多档调节，锻炼全身'},
            {'title': '乒乓球拍', 'price': 40, 'condition': 'good', 'description': '专业乒乓球拍，胶皮完好，手感佳'},
            {'title': '运动水壶', 'price': 20, 'condition': 'like_new', 'description': '大容量运动水壶，保温保冷，便携设计'},
        ]
    },
    {
        'name': '学习用品',
        'description': '文具、办公设备等',
        'color': (155, 89, 182),  # 紫色
        'products': [
            {'title': '笔记本支架', 'price': 45, 'condition': 'good', 'description': '铝合金支架，可调节角度，散热良好'},
            {'title': '机械键盘', 'price': 180, 'condition': 'good', 'description': '青轴机械键盘，手感舒适，RGB背光'},
            {'title': '无线鼠标', 'price': 65, 'condition': 'like_new', 'description': '静音无线鼠标，精准定位，续航持久'},
            {'title': '台灯', 'price': 55, 'condition': 'good', 'description': 'LED护眼台灯，多档调光，USB供电'},
            {'title': '文具收纳盒', 'price': 25, 'condition': 'good', 'description': '多层文具收纳，节省桌面空间'},
            {'title': '计算器', 'price': 30, 'condition': 'good', 'description': '科学计算器，功能全面，适合理工科'},
            {'title': 'U盘 64GB', 'price': 35, 'condition': 'good', 'description': '高速U盘，金属外壳，便携存储'},
            {'title': '移动电源', 'price': 50, 'condition': 'good', 'description': '10000mAh移动电源，快充支持，多设备兼容'},
            {'title': '蓝牙耳机', 'price': 75, 'condition': 'good', 'description': '真无线蓝牙耳机，音质清晰，续航持久'},
            {'title': '笔记本', 'price': 15, 'condition': 'good', 'description': 'A5笔记本，厚本设计，适合做笔记'},
        ]
    }
]

# 用户数据
USERS = [
    {'username': 'student1', 'email': 'student1@campus.edu', 'password': 'password123'},
    {'username': 'student2', 'email': 'student2@campus.edu', 'password': 'password123'},
    {'username': 'student3', 'email': 'student3@campus.edu', 'password': 'password123'},
    {'username': 'student4', 'email': 'student4@campus.edu', 'password': 'password123'},
    {'username': 'student5', 'email': 'student5@campus.edu', 'password': 'password123'},
    {'username': 'student6', 'email': 'student6@campus.edu', 'password': 'password123'},
    {'username': 'student7', 'email': 'student7@campus.edu', 'password': 'password123'},
    {'username': 'student8', 'email': 'student8@campus.edu', 'password': 'password123'},
    {'username': 'student9', 'email': 'student9@campus.edu', 'password': 'password123'},
    {'username': 'student10', 'email': 'student10@campus.edu', 'password': 'password123'},
]

# 知识库数据
KNOWLEDGE_BASE = [
    {
        'knowledge_type': 'faq',
        'title': '如何发布商品？',
        'content': '登录后点击"发布商品"按钮，填写商品信息（标题、描述、价格、图片等），选择商品分类，点击提交即可发布商品。',
        'keywords': '发布,商品,上传,卖东西'
    },
    {
        'knowledge_type': 'faq',
        'title': '如何联系卖家？',
        'content': '在商品详情页面点击"联系卖家"按钮，可以发送消息给卖家，也可以查看卖家留下的联系方式。',
        'keywords': '联系,卖家,沟通,咨询'
    },
    {
        'knowledge_type': 'rule',
        'title': '平台交易规则',
        'content': '1. 禁止发布违禁品和假冒伪劣商品\n2. 交易双方应诚实守信\n3. 禁止恶意刷单和虚假交易\n4. 交易纠纷可联系平台客服',
        'keywords': '规则,交易,禁止,诚信'
    },
    {
        'knowledge_type': 'tip',
        'title': '交易安全提示',
        'content': '1. 尽量选择校内面交\n2. 不要提前支付全款\n3. 保留交易凭证\n4. 发现异常及时举报\n5. 使用平台担保交易更安全',
        'keywords': '安全,提示,防骗,担保'
    },
    {
        'knowledge_type': 'faq',
        'title': '如何修改商品信息？',
        'content': '登录后进入"我的发布"，找到要修改的商品，点击"编辑"按钮即可修改商品信息。已售出的商品无法修改。',
        'keywords': '修改,编辑,商品信息,更新'
    },
    {
        'knowledge_type': 'faq',
        'title': '如何删除商品？',
        'content': '登录后进入"我的发布"，找到要删除的商品，点击"删除"按钮即可。删除后商品将不再显示，无法恢复。',
        'keywords': '删除,下架,商品,移除'
    },
    {
        'knowledge_type': 'rule',
        'title': '商品发布规范',
        'content': '1. 商品描述真实准确\n2. 图片清晰无水印\n3. 价格合理公道\n4. 分类选择正确\n5. 联系方式有效',
        'keywords': '规范,发布,要求,标准'
    },
    {
        'knowledge_type': 'tip',
        'title': '提高商品成交率技巧',
        'content': '1. 拍摄多角度清晰图片\n2. 详细描述商品状况\n3. 设置合理价格\n4. 及时回复买家咨询\n5. 保持良好信誉',
        'keywords': '技巧,成交率,卖得快,建议'
    },
]

def generate_placeholder_image(text, filename, color):
    """生成占位符图片"""
    try:
        img = Image.new('RGB', (400, 300), color=color)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            try:
                font = ImageFont.truetype("msyh.ttc", 24)
            except:
                font = ImageFont.load_default()
        
        text_width, text_height = draw.textsize(text, font=font)
        position = ((400 - text_width) // 2, (300 - text_height) // 2)
        draw.text(position, text, fill=(255, 255, 255), font=font)
        
        # 确保media/products目录存在
        media_dir = os.path.join(os.path.dirname(__file__), 'media', 'products')
        os.makedirs(media_dir, exist_ok=True)
        
        filepath = os.path.join(media_dir, filename)
        img.save(filepath, 'JPEG', quality=85)
        return f'products/{filename}'
    except Exception as e:
        print(f'生成占位图失败: {text}, 错误: {e}')
        return None

def create_users():
    """创建用户"""
    print('创建用户...')
    users = []
    for user_data in USERS:
        try:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password']
            )
            users.append(user)
            print(f'  创建用户: {user.username}')
        except Exception as e:
            print(f'  创建用户失败: {user_data["username"]}, 错误: {e}')
    return users

def create_categories_and_products(users):
    """创建分类和商品"""
    print('创建分类和商品...')
    categories = []
    products = []
    
    for category_data in CATEGORIES:
        try:
            category = Category.objects.create(
                name=category_data['name'],
                description=category_data['description']
            )
            categories.append(category)
            print(f'  创建分类: {category.name}')
            
            for product_data in category_data['products']:
                seller = random.choice(users)
                
                # 生成占位图
                image_filename = f"{product_data['title'][:10]}_{random.randint(1000, 9999)}.jpg"
                image_path = generate_placeholder_image(product_data['title'], image_filename, category_data['color'])
                
                product = Product.objects.create(
                    title=product_data['title'],
                    description=product_data['description'],
                    price=product_data['price'],
                    category=category,
                    seller=seller,
                    condition=product_data['condition'],
                    status=random.choice(['available', 'available', 'available', 'sold', 'reserved']),
                    location=random.choice(['图书馆', '食堂', '宿舍楼下', '教学楼', '体育馆']),
                    contact_info=f'微信: {random.randint(10000, 99999)}',
                    image=image_path,
                    views=random.randint(10, 500)
                )
                products.append(product)
                print(f'    创建商品: {product.title} - ¥{product.price}')
                
        except Exception as e:
            print(f'  创建分类失败: {category_data["name"]}, 错误: {e}')
    
    return categories, products

def create_transactions(users, products):
    """创建交易记录"""
    print('创建交易记录...')
    transactions = []
    
    available_products = [p for p in products if p.status == 'available']
    
    for i in range(min(15, len(available_products))):
        try:
            product = random.choice(available_products)
            buyer = random.choice([u for u in users if u != product.seller])
            
            status = random.choice(['pending', 'confirmed', 'completed', 'cancelled'])
            transaction = Transaction.objects.create(
                buyer=buyer,
                seller=product.seller,
                product=product,
                price=product.price,
                status=status
            )
            
            if status == 'confirmed':
                transaction.confirmed_at = timezone.now() - timedelta(days=random.randint(1, 7))
            elif status == 'completed':
                transaction.confirmed_at = timezone.now() - timedelta(days=random.randint(8, 14))
                transaction.completed_at = timezone.now() - timedelta(days=random.randint(1, 7))
                product.status = 'sold'
                product.save()
            
            transactions.append(transaction)
            print(f'  创建交易: {buyer.username} 购买 {product.title}')
            
        except Exception as e:
            print(f'  创建交易失败, 错误: {e}')
    
    return transactions

def create_reviews(users, products):
    """创建评价"""
    print('创建评价...')
    reviews = []
    
    for i in range(20):
        try:
            reviewer = random.choice(users)
            product = random.choice(products)
            reviewed_user = product.seller
            
            if reviewer == reviewed_user:
                continue
                
            review = Review.objects.create(
                reviewer=reviewer,
                reviewed_user=reviewed_user,
                product=product,
                rating=random.randint(3, 5),
                comment=random.choice([
                    '商品质量很好，和描述一致',
                    '卖家很诚信，交易愉快',
                    '性价比很高，推荐购买',
                    '发货及时，包装完好',
                    '商品成色比预期好',
                    '沟通顺畅，服务态度好',
                    '物美价廉，非常满意',
                    '诚信卖家，值得信赖'
                ])
            )
            reviews.append(review)
            print(f'  创建评价: {reviewer.username} 对 {reviewed_user.username} 的评价')
            
        except Exception as e:
            print(f'  创建评价失败, 错误: {e}')
    
    return reviews

def create_favorites(users, products):
    """创建收藏"""
    print('创建收藏...')
    favorites = []
    
    for i in range(30):
        try:
            user = random.choice(users)
            product = random.choice(products)
            
            favorite, created = Favorite.objects.get_or_create(
                user=user,
                product=product
            )
            if created:
                favorites.append(favorite)
                print(f'  创建收藏: {user.username} 收藏 {product.title}')
                
        except Exception as e:
            print(f'  创建收藏失败, 错误: {e}')
    
    return favorites

def create_messages(users, products):
    """创建消息"""
    print('创建消息...')
    messages = []
    
    for i in range(25):
        try:
            sender = random.choice(users)
            product = random.choice(products)
            receiver = product.seller
            
            if sender == receiver:
                continue
                
            message = Message.objects.create(
                sender=sender,
                receiver=receiver,
                product=product,
                content=random.choice([
                    '请问这个商品还在吗？',
                    '价格可以商量吗？',
                    '可以看看实物吗？',
                    '什么时候方便面交？',
                    '商品成色怎么样？',
                    '能便宜一点吗？',
                    '我想要这个商品',
                    '请问在哪里交易？'
                ])
            )
            messages.append(message)
            print(f'  创建消息: {sender.username} -> {receiver.username}')
            
        except Exception as e:
            print(f'  创建消息失败, 错误: {e}')
    
    return messages

def create_user_behaviors(users, products):
    """创建用户行为"""
    print('创建用户行为...')
    behaviors = []
    
    action_types = ['login', 'logout', 'browse', 'click', 'submit', 'transaction', 'favorite', 'message', 'review', 'other']
    
    for i in range(100):
        try:
            user = random.choice(users)
            action_time = timezone.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            behavior = UserBehavior.objects.create(
                user=user,
                action_type=random.choice(action_types),
                action_time=action_time,
                ip_address=f'192.168.1.{random.randint(1, 255)}',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                referer=random.choice(['', '/home/', '/products/', '/categories/']),
                action_data=json.dumps({'product_id': random.choice(products).id}),
                session_id=f'session_{random.randint(10000, 99999)}'
            )
            behaviors.append(behavior)
            
        except Exception as e:
            print(f'  创建用户行为失败, 错误: {e}')
    
    return behaviors

def create_knowledge_base():
    """创建知识库"""
    print('创建知识库...')
    knowledge_items = []
    
    for kb_data in KNOWLEDGE_BASE:
        try:
            knowledge = Knowledge.objects.create(
                knowledge_type=kb_data['knowledge_type'],
                title=kb_data['title'],
                content=kb_data['content'],
                keywords=kb_data['keywords']
            )
            knowledge_items.append(knowledge)
            print(f'  创建知识库: {knowledge.title}')
            
        except Exception as e:
            print(f'  创建知识库失败: {kb_data["title"]}, 错误: {e}')
    
    return knowledge_items

def create_user_preferences(users, categories):
    """创建用户偏好"""
    print('创建用户偏好...')
    preferences = []
    
    for user in users:
        for category in random.sample(categories, random.randint(1, 3)):
            try:
                preference = UserPreference.objects.create(
                    user=user,
                    category=category,
                    preference_score=random.uniform(0.5, 1.0)
                )
                preferences.append(preference)
                print(f'  创建用户偏好: {user.username} -> {category.name}')
                
            except Exception as e:
                print(f'  创建用户偏好失败, 错误: {e}')
    
    return preferences

def main():
    """主函数"""
    print('=' * 50)
    print('开始生成校园二手交易平台数据')
    print('=' * 50)
    
    try:
        users = create_users()
        categories, products = create_categories_and_products(users)
        transactions = create_transactions(users, products)
        reviews = create_reviews(users, products)
        favorites = create_favorites(users, products)
        messages = create_messages(users, products)
        behaviors = create_user_behaviors(users, products)
        knowledge_items = create_knowledge_base()
        preferences = create_user_preferences(users, categories)
        
        print('=' * 50)
        print('数据生成完成！')
        print(f'用户数量: {len(users)}')
        print(f'分类数量: {len(categories)}')
        print(f'商品数量: {len(products)}')
        print(f'交易数量: {len(transactions)}')
        print(f'评价数量: {len(reviews)}')
        print(f'收藏数量: {len(favorites)}')
        print(f'消息数量: {len(messages)}')
        print(f'用户行为数量: {len(behaviors)}')
        print(f'知识库数量: {len(knowledge_items)}')
        print(f'用户偏好数量: {len(preferences)}')
        print('=' * 50)
        
    except Exception as e:
        print(f'数据生成失败: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()