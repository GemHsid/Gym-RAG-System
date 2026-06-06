from django.urls import path
from .views import ChatAPIView, ChatHistoryView, BotConfigView

urlpatterns = [
    path('config/', BotConfigView.as_view(), name='bot_config'),
    path('chat/', ChatAPIView.as_view(), name='chat_api'),
    path('history/', ChatHistoryView.as_view(), name='chat_history'),
]
