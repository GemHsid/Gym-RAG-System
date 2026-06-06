from django.db import models
from django.conf import settings

class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_sessions", verbose_name="用户")
    topic = models.CharField(max_length=100, default="新对话", verbose_name="会话主题")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "AI对话会话"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.topic}"

class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ('user', '用户'),
        ('ai', 'AI助手'),
    )
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages", verbose_name="所属会话")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="角色")
    content = models.TextField(verbose_name="消息内容")
    retrieved_context = models.TextField(blank=True, default="", verbose_name="检索上下文")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发送时间")

    class Meta:
        verbose_name = "对话消息"
        verbose_name_plural = verbose_name
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:20]}..."
