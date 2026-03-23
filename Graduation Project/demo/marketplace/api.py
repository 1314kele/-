from rest_framework import serializers, viewsets
from .models import Knowledge
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response

# 知识库序列化器
class KnowledgeSerializer(serializers.ModelSerializer):
    """知识库序列化器"""
    class Meta:
        model = Knowledge
        fields = ['id', 'knowledge_type', 'title', 'content', 'keywords', 'create_time', 'update_time']

# 知识库视图集
class KnowledgeViewSet(viewsets.ModelViewSet):
    """知识库视图集"""
    queryset = Knowledge.objects.all()
    serializer_class = KnowledgeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['knowledge_type']
    search_fields = ['title', 'content', 'keywords']
    
    def get_permissions(self):
        """根据动作获取权限"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """根据知识类型获取知识"""
        knowledge_type = request.query_params.get('knowledge_type')
        if not knowledge_type:
            return Response({'error': 'knowledge_type is required'}, status=400)
        
        knowledge_items = Knowledge.objects.filter(knowledge_type=knowledge_type)
        serializer = self.get_serializer(knowledge_items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """搜索知识"""
        query = request.query_params.get('q')
        if not query:
            return Response({'error': 'q is required'}, status=400)
        
        knowledge_items = Knowledge.objects.filter(
            models.Q(title__icontains=query) |
            models.Q(content__icontains=query) |
            models.Q(keywords__icontains=query)
        )
        serializer = self.get_serializer(knowledge_items, many=True)
        return Response(serializer.data)

# 导入models
import django.db.models as models