from django.core.management.base import BaseCommand

from common.demo_content import (
    ensure_demo_courses,
    ensure_demo_equipment,
    ensure_demo_membership_products,
)


class Command(BaseCommand):
    help = "写入论文演示阶段使用的门店、课程、器械和会员卡示例数据"

    def handle(self, *args, **options):
        products = ensure_demo_membership_products()
        equipment = ensure_demo_equipment()
        courses = ensure_demo_courses(days=7)
        self.stdout.write(
            self.style.SUCCESS(
                f"示例数据已准备完成：会员卡 {len(products)} 个，器械 {len(equipment)} 个，课程 {len(courses)} 节。"
            )
        )
