"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from marketplace import views as marketplace_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('marketplace.urls')),
    # 添加Django认证URLs
    path('accounts/', include('django.contrib.auth.urls')),
    # 手动定义登录URL，使用自定义登录视图
    path('login/', marketplace_views.login, name='login'),
    # 手动定义退出登录URL，使用'logout'名称
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]

# 开发环境下的媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)