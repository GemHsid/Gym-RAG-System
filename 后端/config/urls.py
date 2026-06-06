"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.shortcuts import redirect
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from common.views import CustomLoginView, GymGuideView, HomeInfoView, CourseScheduleView
from common.dashboard import dashboard
from fitness.views import EquipmentRepairCreateView

# 自定义 Admin 站点头部信息
admin.site.site_header = '铁馆管理后台'
admin.site.site_title = '铁馆管理后台'
admin.site.index_title = '铁馆管理后台'

urlpatterns = [
    # 根路径重定向到 Admin 登录页
    path("", lambda request: redirect("/admin/login/")),
    
    # 自定义登录页 (覆盖 admin 的默认登录)
    path('admin/login/', CustomLoginView.as_view(), name='login'),

    # 管理后台看板页 (嵌入 Admin 首页)
    path('dashboard/', dashboard, name='dashboard'),
    
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/fitness/", include("fitness.urls")),
    path("api/bot/", include("bot.urls")),
    path("api/orders/", include("orders.urls")),
    path("api/equipment/repair/", EquipmentRepairCreateView.as_view(), name="equipment_repair"),
    path("api/gym/guide/", GymGuideView.as_view(), name="gym_guide"),
    path("api/home/info/", HomeInfoView.as_view(), name="home_info"),
    path("api/courses/schedule/", CourseScheduleView.as_view(), name="course_schedule"),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
