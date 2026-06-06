from django.apps import AppConfig
import os

class FitnessConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "fitness"
    verbose_name = "场馆运营"

    def ready(self):
        # 避免在收集静态文件或迁移时执行
        if os.environ.get('RUN_MAIN') == 'true':
            import fitness.signals  # noqa
