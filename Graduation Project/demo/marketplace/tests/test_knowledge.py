from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Knowledge

class KnowledgeTest(TestCase):
    """知识库模块测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        
        # 创建测试知识库条目
        self.knowledge = Knowledge.objects.create(
            knowledge_type='faq',
            title='测试问题',
            content='测试内容',
            keywords='测试,问题'
        )
    
    def test_knowledge_creation(self):
        """测试知识库条目创建"""
        self.assertEqual(self.knowledge.title, '测试问题')
        self.assertEqual(self.knowledge.knowledge_type, 'faq')
        self.assertEqual(self.knowledge.content, '测试内容')
        self.assertEqual(self.knowledge.keywords, '测试,问题')
    
    def test_knowledge_str_representation(self):
        """测试知识库条目字符串表示"""
        expected_str = self.knowledge.title
        self.assertEqual(str(self.knowledge), expected_str)
    
    def test_knowledge_query(self):
        """测试知识库查询"""
        # 按类型查询
        faq_knowledge = Knowledge.objects.filter(knowledge_type='faq')
        self.assertEqual(faq_knowledge.count(), 1)
        
        # 按关键词查询
        keyword_knowledge = Knowledge.objects.filter(keywords__icontains='测试')
        self.assertEqual(keyword_knowledge.count(), 1)
    
    def test_knowledge_update(self):
        """测试知识库更新"""
        self.knowledge.title = '更新后的问题'
        self.knowledge.save()
        updated_knowledge = Knowledge.objects.get(id=self.knowledge.id)
        self.assertEqual(updated_knowledge.title, '更新后的问题')
    
    def test_knowledge_delete(self):
        """测试知识库删除"""
        knowledge_id = self.knowledge.id
        self.knowledge.delete()
        with self.assertRaises(Knowledge.DoesNotExist):
            Knowledge.objects.get(id=knowledge_id)