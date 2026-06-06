import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from fitness.models import Equipment

for eq in Equipment.objects.all():
    eq.gif_url = "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1470&auto=format&fit=crop"
    eq.save()
print("Fixed Equipment gif_url")