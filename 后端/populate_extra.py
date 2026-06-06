import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from orders.models import MembershipProduct
from fitness.models import TeamMember, Course
from users.models import UserProfile

def run():
    # 会员卡
    p1, _ = MembershipProduct.objects.get_or_create(
        name="基础月卡",
        defaults={"price": Decimal("199.00"), "original_price": Decimal("299.00"), "is_promotion": True, "days_duration": 30, "tags": ["畅练", "洗浴"]}
    )
    p2, _ = MembershipProduct.objects.get_or_create(
        name="年度VIP卡",
        defaults={"price": Decimal("1999.00"), "original_price": Decimal("2599.00"), "is_promotion": True, "days_duration": 365, "tags": ["畅练", "免费私教1节"]}
    )
    print("会员卡产品已创建。")

    # 教练
    coach, _ = TeamMember.objects.get_or_create(
        name="李教练",
        defaults={"role": "coach", "phone": "13800138000", "bio": "资深健身教练，拥有8年执教经验"}
    )
    print("教练已创建。")

    # 课程
    start_t = timezone.now() + timedelta(days=1)
    Course.objects.get_or_create(
        name="燃脂单车课",
        defaults={"coach": coach, "coach_name": coach.name, "start_time": start_t, "duration": 45, "capacity": 15, "booked_count": 0}
    )
    Course.objects.get_or_create(
        name="普拉提塑形",
        defaults={"coach": coach, "coach_name": coach.name, "start_time": start_t + timedelta(hours=2), "duration": 60, "capacity": 10, "booked_count": 0}
    )
    print("课程排期已创建。")

    # 给用户加余额
    users = UserProfile.objects.all()
    for u in users:
        u.balance = Decimal("5000.00")
        u.save()
    print("已为所有测试用户充值测试余额。")

if __name__ == '__main__':
    run()