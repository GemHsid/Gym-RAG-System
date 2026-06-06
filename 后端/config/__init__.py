import os
from django.utils import timezone
import django
from django.conf import settings

# 设置服务器启动时间环境变量
try:
    if not settings.configured:
        import config.settings
        django.conf.settings.configure(default_settings=config.settings)
    
    # 简单的设置启动时间，不需要复杂的 Django 环境检查
    os.environ['SERVER_START_TIME'] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
except:
    # Fallback if django is not yet fully loaded
    import datetime
    os.environ['SERVER_START_TIME'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
