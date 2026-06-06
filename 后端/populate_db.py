import os
import django

# 1. 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from fitness.models import BodyPart, Equipment
from django.contrib.auth import get_user_model

User = get_user_model()

def populate():
    print("开始填充测试数据...")
    parts_data = ["胸部", "背部", "腿部", "肩部", "有氧"]
    parts = {}
    for name in parts_data:
        part, created = BodyPart.objects.get_or_create(name=name)
        parts[name] = part
        if created:
            print(f"  [+] 创建部位: {name}")
        else:
            print(f"  [.] 部位已存在: {name}")
    equipments_data = [
        {
            "name": "坐姿推胸机",
            "part": "胸部",
            "description": "适合胸部推举训练，帮助提升胸大肌与肱三头肌力量。",
            "target_muscles": "胸大肌, 肱三头肌, 三角肌前束",
            "precautions": "座椅高度与把手齐平，肩部保持下沉，推起时不要锁死肘关节。",
            "location": "A区-01",
            "status": Equipment.STATUS_IDLE,
            "gif_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1470&auto=format&fit=crop"
        },
        {
            "name": "高位下拉",
            "part": "背部",
            "description": "经典背部训练器械，适合背阔肌下拉发力。",
            "target_muscles": "背阔肌, 肱二头肌, 菱形肌",
            "precautions": "避免身体后仰借力，下拉至锁骨附近即可，肩部不耸肩。",
            "location": "B区-02",
            "status": Equipment.STATUS_IDLE,
            "gif_url": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1470&auto=format&fit=crop"
        },
        {
            "name": "倒蹬机",
            "part": "腿部",
            "description": "适合下肢大重量训练，强化腿部与臀部力量。",
            "target_muscles": "股四头肌, 臀大肌, 腘绳肌",
            "precautions": "双脚与肩同宽，下降时膝盖朝脚尖方向，不要塌腰。",
            "location": "C区-01",
            "status": Equipment.STATUS_IDLE,
            "gif_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?q=80&w=1470&auto=format&fit=crop"
        },
        {
            "name": "史密斯机",
            "part": "腿部",
            "description": "可进行深蹲、卧推、肩推等复合动作训练。",
            "target_muscles": "股四头肌, 胸大肌, 三角肌, 臀大肌",
            "precautions": "确认卡扣回位后再装卸杠铃片，训练时优先使用保护挡位。",
            "location": "C区-03",
            "status": Equipment.STATUS_IN_USE,
            "gif_url": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=1470&auto=format&fit=crop"
        },
        {
            "name": "坐姿推肩机",
            "part": "肩部",
            "description": "帮助三角肌完成稳定推举，适合肩部孤立训练。",
            "target_muscles": "三角肌前束, 三角肌中束, 肱三头肌",
            "precautions": "保持核心收紧，推起时手腕中立，不要含胸耸肩。",
            "location": "D区-01",
            "status": Equipment.STATUS_IDLE,
            "gif_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=1470&auto=format&fit=crop"
        },
        {
            "name": "跑步机",
            "part": "有氧",
            "description": "支持有氧热身、减脂跑与心肺耐力训练。",
            "target_muscles": "股四头肌, 小腿, 臀部, 心肺系统",
            "precautions": "先低速起步再逐步提速，训练结束后缓速走1到2分钟。",
            "location": "有氧区-05",
            "status": Equipment.STATUS_MAINTENANCE,
            "gif_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?q=80&w=1470&auto=format&fit=crop"
        }
    ]

    for item in equipments_data:
        part = parts.get(item["part"])
        if part:
            obj, created = Equipment.objects.get_or_create(
                name=item["name"],
                defaults={
                    "part": part,
                    "description": item["description"],
                    "target_muscles": item["target_muscles"],
                    "precautions": item["precautions"],
                    "location": item["location"],
                    "status": item["status"],
                    "gif_url": item["gif_url"]
                }
            )
            if not created:
                obj.part = part
                obj.description = item["description"]
                obj.target_muscles = item["target_muscles"]
                obj.precautions = item["precautions"]
                obj.location = item["location"]
                obj.status = item["status"]
                obj.gif_url = item["gif_url"]
                obj.save()
            if created:
                print(f"  [+] 创建器械: {item['name']}")
            else:
                print(f"  [√] 更新器械: {item['name']}")

    openid = "test_user_001"
    user, created = User.objects.get_or_create(
        username=openid,
        defaults={
            "openid": openid,
            "nickname": "Jack测试",
            "balance": 100
        }
    )
    if created:
        user.set_unusable_password()
        user.save()
        print(f"  [+] 创建用户: {user.nickname} (ID: {user.id})")
    else:
        print(f"  [.] 用户已存在: {user.nickname} (ID: {user.id})")

    print("数据填充完成！")

if __name__ == '__main__':
    populate()
