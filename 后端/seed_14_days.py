import os
import sys
import django
import random
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.models import MembershipProduct, Order
from fitness.models import CheckIn, EquipmentUsage, Course, Booking
from bot.models import ChatSession, ChatMessage

User = get_user_model()

def run():
    print("1. 清理之前不合理的测试数据...")
    
    # 清理之前用脚本生成的僵尸数据
    User.objects.filter(username__startswith="seed_user_").delete()
    User.objects.filter(username="test_seed_user").delete()
    Order.objects.filter(out_trade_no__startswith="SEED_").delete()
    
    # 将所有的签到、聊天和预约记录清理，确保看板数据彻底重置干净
    CheckIn.objects.all().delete()
    ChatSession.objects.all().delete()
    Booking.objects.all().delete()

    print("2. 创建 30 名独立的真实模拟会员...")
    users = []
    for i in range(1, 31):
        u, created = User.objects.get_or_create(
            username=f"seed_user_{i}",
            defaults={
                "openid": f"seed_openid_{i}_{random.randint(1000,9999)}",
                "nickname": f"健身达人_{i}号",
                "balance": Decimal(random.randint(100, 2000)),
                "is_face_verified": random.choice([True, False])
            }
        )
        users.append(u)

    products = list(MembershipProduct.objects.all())
    if not products:
        p, _ = MembershipProduct.objects.get_or_create(name="月卡", price=Decimal("199.00"), days_duration=30)
        products.append(p)
        
    courses = list(Course.objects.all())

    print("3. 开始按真实逻辑生成过去14天业务数据...")
    now = timezone.now()

    chat_topics = [
        ("怎么使用史密斯机？", "史密斯机的使用方法如下：首先调整好杠铃的高度，确保卡扣能安全挂住。然后再进行推举或深蹲。"),
        ("推荐一个减脂计划", "减脂建议多做有氧，比如每次力量训练后加入30分钟跑步机或椭圆机。饮食注意热量缺口。"),
        ("场馆营业时间", "我们是24小时营业的，随时欢迎您来锻炼。夜间请注意安全。"),
        ("怎么预约瑜伽课", "您可以在小程序首页点击【课程预约】，选择适合您的时间段和教练即可。"),
        ("跑步机怎么调坡度", "跑步机左侧把手有坡度调节按键，或者在中控面板上直接输入坡度数值。"),
        ("腹肌怎么练", "腹肌可以通过卷腹、仰卧举腿、俄罗斯挺身等动作来锻炼，记得配合减脂才能看出线条。")
    ]

    for day_offset in range(14, -1, -1):
        current_day = now - timedelta(days=day_offset)
        
        # a. 每天产生 1-4 笔订单 (分散到不同用户，更真实)
        daily_orders = random.randint(1, 4)
        for _ in range(daily_orders):
            u = random.choice(users)
            p = random.choice(products)
            order = Order.objects.create(
                user=u, product=p, amount=p.price, status='paid',
                out_trade_no=f"SEED_{current_day.strftime('%Y%m%d%H%M%S')}_{random.randint(1000,9999)}"
            )
            Order.objects.filter(id=order.id).update(created_at=current_day)
            
        # b. 每天产生 15-30 次打卡入场 (模拟每天的真实人流)
        daily_checkins = random.randint(15, 30)
        for _ in range(daily_checkins):
            u = random.choice(users)
            # 随机生成当天的某个时间点作为入场时间
            hour = random.randint(8, 22)
            minute = random.randint(0, 59)
            checkin_t = current_day.replace(hour=hour, minute=minute)
            
            method = 'face' if u.is_face_verified else random.choice(['qr', 'manual'])
            checkin = CheckIn.objects.create(user=u, method=method)
            
            # 如果是今天，且生成的时间在当前时间之前不久，可能还没离场 (模拟"当前在馆")
            # 在馆人数控制在 5-15 人左右比较合理
            is_today = (day_offset == 0)
            if is_today and checkin_t > (now - timedelta(hours=1.5)) and checkin_t < now:
                # 仍在馆内，不设置 checkout_time
                CheckIn.objects.filter(id=checkin.id).update(checkin_time=checkin_t)
            else:
                # 已经离场，锻炼时间 45 到 120 分钟
                duration = timedelta(minutes=random.randint(45, 120))
                checkout_t = checkin_t + duration
                if checkout_t > now:
                    checkout_t = now
                CheckIn.objects.filter(id=checkin.id).update(checkin_time=checkin_t, checkout_time=checkout_t)
                
        # c. AI问答 (每天 5-12 次真实对话)
        daily_chats = random.randint(5, 12)
        for _ in range(daily_chats):
            u = random.choice(users)
            topic, reply = random.choice(chat_topics)
            session = ChatSession.objects.create(user=u, topic=topic)
            ChatSession.objects.filter(id=session.id).update(created_at=current_day)
            
            msg1 = ChatMessage.objects.create(session=session, role="user", content=topic)
            msg2 = ChatMessage.objects.create(session=session, role="ai", content=reply)
            ChatMessage.objects.filter(id__in=[msg1.id, msg2.id]).update(created_at=current_day)

        # d. 课程预约 (分散预约，防超卖模拟)
        if courses and random.random() < 0.8:
            c = random.choice(courses)
            # 每天有 2-8 人预约课程
            for _ in range(random.randint(2, 8)):
                u = random.choice(users)
                if not Booking.objects.filter(user=u, course=c).exists():
                    booking = Booking.objects.create(user=u, course=c, status='booked')
                    Booking.objects.filter(id=booking.id).update(created_at=current_day)

    print("数据重置与生成完毕！现在的订单数、在馆人数、AI对话分布更加真实合理。")

if __name__ == "__main__":
    run()
