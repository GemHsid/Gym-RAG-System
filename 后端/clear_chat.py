import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from bot.models import ChatSession, ChatMessage

count_msg, _ = ChatMessage.objects.all().delete()
count_session, _ = ChatSession.objects.all().delete()
print(f"Deleted {count_msg} messages and {count_session} sessions.")