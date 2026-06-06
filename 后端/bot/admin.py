from django.contrib import admin
from .models import ChatSession, ChatMessage

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'topic', 'latest_user_message', 'latest_ai_message', 'latest_message_time', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'topic')

    def latest_user_message(self, obj):
        message = obj.messages.filter(role='user').order_by('-created_at').first()
        if not message:
            return '-'
        return message.content[:40] + '...' if len(message.content) > 40 else message.content
    latest_user_message.short_description = '最新用户消息'

    def latest_ai_message(self, obj):
        message = obj.messages.filter(role='ai').order_by('-created_at').first()
        if not message:
            return '-'
        return message.content[:40] + '...' if len(message.content) > 40 else message.content
    latest_ai_message.short_description = '最新AI回复'

    def latest_message_time(self, obj):
        message = obj.messages.order_by('-created_at').first()
        return message.created_at if message else '-'
    latest_message_time.short_description = '最新消息时间'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'role', 'short_content', 'short_context', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content',)

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = '内容摘要'

    def short_context(self, obj):
        if not obj.retrieved_context:
            return '-'
        return obj.retrieved_context[:50] + '...' if len(obj.retrieved_context) > 50 else obj.retrieved_context
    short_context.short_description = '检索上下文'
