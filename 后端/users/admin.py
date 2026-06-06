from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import UserProfile, Feedback
from common.admin_mixins import ExportExcelMixin

@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin, ExportExcelMixin):
    list_display = ('username', 'nickname', 'phone', 'balance', 'membership_expiry', 'ai_usage', 'action_buttons')
    search_fields = ('username', 'nickname', 'phone', 'openid')
    list_filter = ('is_face_verified', 'is_staff', 'is_superuser', 'groups')
    actions = ['export_as_excel']
    
    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('openid', 'nickname', 'avatar', 'phone', 'face_image', 'is_face_verified', 'balance', 'membership_expiry')}),
    )

    # 新增字段展示：AI使用情况 (Mock数据)
    @admin.display(description='AI活跃度')
    def ai_usage(self, obj):
        # 模拟计算活跃度，实际应从 ChatSession 统计
        interaction_count = obj.chat_sessions.count() * 5 + 10 # Mock calculation
        if interaction_count > 100: interaction_count = 100
        
        color = "#4caf50" # Green
        if interaction_count < 30: color = "#ff9800" # Orange
        if interaction_count < 10: color = "#f44336" # Red
        
        return format_html(
            '<div style="width: 100px; background-color: #eee; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; height: 10px; background-color: {};"></div>'
            '</div>',
            interaction_count, color
        )

    # 增强操作按钮
    @admin.display(description='快捷操作')
    def action_buttons(self, obj):
        return format_html(
            '''
            <div style="display: flex; gap: 8px;">
                <a href="{}" style="display: inline-block; padding: 4px 10px; background-color: #8B3A3A; color: #ffffff !important; border-radius: 4px; text-decoration: none; font-size: 12px; line-height: 1.5; font-weight: bold;">详情</a>
                <a href="javascript:void(0);" onclick="alert('即将打开与 {} 的AI对话记录')" style="display: inline-block; padding: 4px 10px; background-color: #B08D77; color: #ffffff !important; border-radius: 4px; text-decoration: none; font-size: 12px; line-height: 1.5; font-weight: bold;">AI记录</a>
            </div>
            ''',
            reverse('admin:users_userprofile_change', args=[obj.pk]),
            obj.nickname or obj.username
        )

    # 新增人脸注册功能的上下文 (示例)
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['face_registration_enabled'] = True
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "content")
    actions = ["export_as_excel"]
