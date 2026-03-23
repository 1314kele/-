from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
from marketplace.models import Knowledge
import time
import random

class Command(BaseCommand):
    """采集知识管理命令"""
    help = '采集知识（商品分类标准、交易规则、常见问题等）'
    
    def add_arguments(self, parser):
        parser.add_argument('--source', type=str, default='all', help='采集源（all, university, forum）')
        parser.add_argument('--limit', type=int, default=10, help='采集数量限制')
    
    def handle(self, *args, **options):
        """处理采集任务"""
        source = options['source']
        limit = options['limit']
        
        self.stdout.write(f'开始采集知识，源: {source}, 限制: {limit}')
        
        if source == 'all' or source == 'university':
            self.collect_from_university(limit)
        
        if source == 'all' or source == 'forum':
            self.collect_from_forum(limit)
        
        self.stdout.write('采集完成')
    
    def collect_from_university(self, limit):
        """从高校官网采集"""
        # 模拟高校官网URL（实际项目中替换为真实URL）
        urls = [
            'https://example.com/university/trade_rules',
            'https://example.com/university/product_categories',
            'https://example.com/university/faq',
        ]
        
        count = 0
        for url in urls:
            if count >= limit:
                break
                
            try:
                self.stdout.write(f'采集高校官网: {url}')
                # 模拟采集结果
                knowledge_items = self._mock_university_data(url)
                
                for item in knowledge_items:
                    if count >= limit:
                        break
                    
                    # 检查是否已存在
                    if not Knowledge.objects.filter(
                        title=item['title'],
                        knowledge_type=item['knowledge_type']
                    ).exists():
                        Knowledge.objects.create(**item)
                        self.stdout.write(f'已添加: {item["title"]}')
                        count += 1
                        # 随机延迟，避免被反爬
                        time.sleep(random.uniform(1, 3))
                        
            except Exception as e:
                self.stdout.write(f'采集失败: {str(e)}')
    
    def collect_from_forum(self, limit):
        """从校园论坛采集"""
        # 模拟校园论坛URL
        urls = [
            'https://example.com/forum/trade_discussions',
            'https://example.com/forum/product_recommendations',
            'https://example.com/forum/faq',
        ]
        
        count = 0
        for url in urls:
            if count >= limit:
                break
                
            try:
                self.stdout.write(f'采集校园论坛: {url}')
                # 模拟采集结果
                knowledge_items = self._mock_forum_data(url)
                
                for item in knowledge_items:
                    if count >= limit:
                        break
                    
                    # 检查是否已存在
                    if not Knowledge.objects.filter(
                        title=item['title'],
                        knowledge_type=item['knowledge_type']
                    ).exists():
                        Knowledge.objects.create(**item)
                        self.stdout.write(f'已添加: {item["title"]}')
                        count += 1
                        # 随机延迟
                        time.sleep(random.uniform(1, 3))
                        
            except Exception as e:
                self.stdout.write(f'采集失败: {str(e)}')
    
    def _mock_university_data(self, url):
        """模拟高校官网数据"""
        if 'trade_rules' in url:
            return [
                {
                    'knowledge_type': 'rule',
                    'title': '校园二手交易管理办法',
                    'content': '为规范校园二手交易行为，维护交易秩序，特制定本办法...',
                    'keywords': '交易规则,管理办法,校园二手',
                },
                {
                    'knowledge_type': 'rule',
                    'title': '商品发布规范',
                    'content': '商品发布需遵守以下规范：1. 如实描述商品状况...',
                    'keywords': '商品发布,规范,交易规则',
                },
            ]
        elif 'product_categories' in url:
            return [
                {
                    'knowledge_type': 'category',
                    'title': '商品分类标准',
                    'content': '校园二手商品分为以下类别：1. 电子产品...',
                    'keywords': '商品分类,标准,类别',
                },
            ]
        elif 'faq' in url:
            return [
                {
                    'knowledge_type': 'faq',
                    'title': '常见问题解答',
                    'content': 'Q: 如何发布商品？A: 登录系统后，点击"发布商品"...',
                    'keywords': '常见问题,FAQ,解答',
                },
            ]
        return []
    
    def _mock_forum_data(self, url):
        """模拟校园论坛数据"""
        if 'trade_discussions' in url:
            return [
                {
                    'knowledge_type': 'rule',
                    'title': '交易安全小贴士',
                    'content': '1. 选择公共场合交易...',
                    'keywords': '交易安全,小贴士,注意事项',
                },
            ]
        elif 'product_recommendations' in url:
            return [
                {
                    'knowledge_type': 'guide',
                    'title': '电子产品选购指南',
                    'content': '选购二手电子产品时应注意：1. 检查外观...',
                    'keywords': '电子产品,选购,指南',
                },
            ]
        elif 'faq' in url:
            return [
                {
                    'knowledge_type': 'faq',
                    'title': '论坛常见问题',
                    'content': 'Q: 如何提高交易成功率？A: 详细描述商品...',
                    'keywords': '论坛,常见问题,交易',
                },
            ]
        return []