from django import forms
from .models import Product, Category, Message, Review

class ProductForm(forms.ModelForm):
    """商品表单"""
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'category', 'condition', 'location', 'latitude', 'longitude', 'contact_info', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0000001', 'placeholder': '纬度 (可选)'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0000001', 'placeholder': '经度 (可选)'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class MessageForm(forms.ModelForm):
    """消息表单"""
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '请输入消息内容...'})
        }

class ReviewForm(forms.ModelForm):
    """评价表单"""
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '请输入评价内容...'})
        }

class SearchForm(forms.Form):
    """搜索表单"""
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索商品...',
            'id': 'search-input'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='所有分类',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '最低价格'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '最高价格'
        })
    )
    
    condition = forms.ChoiceField(
        choices=[('', '所有状况')] + Product.CONDITION_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('', '默认排序'),
            ('price_asc', '价格从低到高'),
            ('price_desc', '价格从高到低'),
            ('views', '浏览量'),
            ('created_at', '发布时间')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )