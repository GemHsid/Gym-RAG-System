import os
import sys
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from fitness.models import TeamMember, Course

def run():
    coach, _ = TeamMember.objects.get_or_create(
        name="李教练",
        defaults={"role": "coach", "phone": "13800138000", "bio": "资深健身教练，拥有8年执教经验"}
    )
    
    coach2, _ = TeamMember.objects.get_or_create(
        name="张教练",
        defaults={"role": "coach", "phone": "13900139000", "bio": "瑜伽普拉提专家"}
    )

    now = timezone.now()
    # 为今天（当前时间）添加几节课
    # 下午 14:00
    Course.objects.get_or_create(
        name="力量训练基础",
        start_time__date=now.date(),
        defaults={"coach": coach, "coach_name": coach.name, "start_time": now.replace(hour=14, minute=0, second=0), "duration": 60, "capacity": 20, "booked_count": 2}
    )
    # 下午 16:30
    Course.objects.get_or_create(
        name="有氧搏击操",
        start_time__date=now.date(),
        defaults={"coach": coach2, "coach_name": coach2.name, "start_time": now.replace(hour=16, minute=30, second=0), "duration": 45, "capacity": 15, "booked_count": 5}
    )
    # 晚上 19:00
    Course.objects.get_or_create(
        name="晚间瑜伽",
        start_time__date=now.date(),
        defaults={"coach": coach2, "coach_name": coach2.name, "start_time": now.replace(hour=19, minute=0, second=0), "duration": 60, "capacity": 10, "booked_count": 1}
    )

    print("今日课程已补充成功！")

if __name__ == '__main__':
    run()