# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# 设置随机种子确保结果可重复
np.random.seed(42)
random.seed(42)

print("=== 开始生成大数据集 ===")

# 1. 生成分类数据 (20个分类)
categories_data = []
category_names = [
    "电子产品", "学习用品", "服装鞋帽", "家居用品", "运动器材",
    "图书杂志", "美妆护肤", "数码配件", "食品饮料", "办公用品",
    "玩具模型", "宠物用品", "汽车配件", "户外装备", "音乐乐器",
    "摄影器材", "游戏设备", "健康保健", "手工艺品", "二手商品"
]

category_descriptions = [
    "各类电子设备和数码产品",
    "学习相关的书籍和文具",
    "服装、鞋子和配饰",
    "家庭日常用品和装饰",
    "体育运动相关器材",
    "各类图书和期刊杂志",
    "美容化妆和护肤产品",
    "手机、电脑等数码配件",
    "食品、饮料和零食",
    "办公文具和设备",
    "玩具、模型和游戏",
    "宠物食品和用品",
    "汽车零配件和装饰",
    "户外运动和露营装备",
    "乐器和音乐相关设备",
    "相机和摄影器材",
    "游戏机和游戏软件",
    "保健品和医疗用品",
    "手工制作的艺术品",
    "二手商品和闲置物品"
]

for i, (name, desc) in enumerate(zip(category_names, category_descriptions), 1):
    categories_data.append({
        '分类ID': i,
        '分类名称': name,
        '分类描述': desc
    })

# 2. 生成用户数据 (200个用户)
users_data = []
cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "武汉", "成都", "西安", "重庆"]
first_names = ["张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
last_names = ["明", "华", "强", "伟", "芳", "娜", "磊", "静", "杰", "婷"]

for i in range(1, 201):
    users_data.append({
        '用户ID': i,
        '用户名': f"user{i:03d}",
        '真实姓名': f"{random.choice(first_names)}{random.choice(last_names)}",
        '城市': random.choice(cities),
        '注册时间': datetime.now() - timedelta(days=random.randint(1, 365))
    })

# 3. 生成商品数据 (1000个商品)
products_data = []
product_templates = [
    ("{}手机", 1000, 5000),
    ("{}笔记本电脑", 3000, 10000),
    ("{}书籍", 20, 100),
    ("{}衣服", 50, 300),
    ("{}鞋子", 100, 500),
    ("{}耳机", 100, 800),
    ("{}手表", 200, 1500),
    ("{}背包", 80, 400),
    ("{}鼠标", 30, 200),
    ("{}键盘", 100, 600)
]

brands = ["苹果", "华为", "小米", "三星", "联想", "戴尔", "耐克", "阿迪达斯", "索尼", "佳能"]

for i in range(1, 1001):
    template = random.choice(product_templates)
    brand = random.choice(brands)
    category_id = random.randint(1, 20)
    price = random.randint(template[1], template[2])
    
    products_data.append({
        '商品ID': i,
        '商品名称': template[0].format(brand),
        '分类ID': category_id,
        '价格': price,
        '卖家ID': random.randint(1, 200),
        '上架时间': datetime.now() - timedelta(days=random.randint(1, 180)),
        '库存数量': random.randint(1, 50)
    })

# 4. 生成收藏数据 (5000条收藏)
favorites_data = []
for i in range(1, 5001):
    favorites_data.append({
        '收藏ID': i,
        '用户ID': random.randint(1, 200),
        '商品ID': random.randint(1, 1000),
        '收藏时间': datetime.now() - timedelta(days=random.randint(1, 90))
    })

# 5. 生成评价数据 (2000条评价)
reviews_data = []
ratings = [1, 2, 3, 4, 5]
review_texts = [
    "商品质量很好，非常满意！",
    "发货速度很快，包装完好",
    "性价比很高，推荐购买",
    "与描述相符，物有所值",
    "服务态度很好，下次还会来",
    "商品有些瑕疵，但还能接受",
    "物流有点慢，其他都不错",
    "价格实惠，质量也不错",
    "卖家很专业，解答详细",
    "整体体验很好，五星好评"
]

for i in range(1, 2001):
    reviews_data.append({
        '评价ID': i,
        '用户ID': random.randint(1, 200),
        '商品ID': random.randint(1, 1000),
        '评分': random.choice(ratings),
        '评价内容': random.choice(review_texts),
        '评价时间': datetime.now() - timedelta(days=random.randint(1, 60))
    })

# 6. 创建DataFrame并保存为Excel
print("=== 创建数据表 ===")

df_categories = pd.DataFrame(categories_data)
df_users = pd.DataFrame(users_data)
df_products = pd.DataFrame(products_data)
df_favorites = pd.DataFrame(favorites_data)
df_reviews = pd.DataFrame(reviews_data)

# 格式化日期列
date_columns = ['注册时间', '上架时间', '收藏时间', '评价时间']
for df in [df_users, df_products, df_favorites, df_reviews]:
    for col in df.columns:
        if '时间' in col:
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

# 保存到Excel文件
excel_file = "marketplace_large_data.xlsx"
print(f"=== 保存数据到 {excel_file} ===")

with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    df_categories.to_excel(writer, sheet_name='分类', index=False)
    df_users.to_excel(writer, sheet_name='用户', index=False)
    df_products.to_excel(writer, sheet_name='商品', index=False)
    df_favorites.to_excel(writer, sheet_name='收藏', index=False)
    df_reviews.to_excel(writer, sheet_name='评价', index=False)

# 显示数据统计
print("=== 数据生成完成 ===")
print(f"分类数据: {len(df_categories)} 条")
print(f"用户数据: {len(df_users)} 条")
print(f"商品数据: {len(df_products)} 条")
print(f"收藏数据: {len(df_favorites)} 条")
print(f"评价数据: {len(df_reviews)} 条")
print(f"总数据量: {len(df_categories) + len(df_users) + len(df_products) + len(df_favorites) + len(df_reviews)} 条")
print(f"Excel文件已保存: {excel_file}")