from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from fitness.models import BodyPart, Equipment, EquipmentRepair, EquipmentUsage


User = get_user_model()


class EquipmentFeatureTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="equipment_tester", password="test123456", openid="equipment_tester")
        self.part = BodyPart.objects.create(name="胸部")
        self.equipment = Equipment.objects.create(
            name="坐姿推胸机",
            part=self.part,
            description="胸部训练器械",
            target_muscles="胸大肌, 肱三头肌",
            precautions="训练前调整座椅高度",
            location="A区-01",
            status=Equipment.STATUS_IDLE,
            gif_url="https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1470&auto=format&fit=crop",
        )

    def test_equipment_list_returns_real_fields(self):
        response = self.client.get(reverse("equipment_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["code"], 0)
        self.assertEqual(response.data["data"][0]["status"], Equipment.STATUS_IDLE)
        self.assertEqual(response.data["data"][0]["status_label"], "空闲")
        self.assertEqual(response.data["data"][0]["target_muscles"], "胸大肌, 肱三头肌")
        self.assertEqual(response.data["data"][0]["precautions"], "训练前调整座椅高度")

    def test_repair_by_equipment_id_sets_maintenance_status(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("equipment_repair"),
            {
                "equipment_id": self.equipment.id,
                "issue_description": "滑轮异响",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["code"], 0)
        self.equipment.refresh_from_db()
        self.assertEqual(self.equipment.status, Equipment.STATUS_MAINTENANCE)
        self.assertEqual(EquipmentRepair.objects.count(), 1)

    def test_usage_start_and_stop_updates_equipment_status(self):
        self.client.force_authenticate(self.user)
        start_response = self.client.post(
            reverse("equipment_usage-start"),
            {"equipment_id": self.equipment.id},
            format="json",
        )
        self.assertEqual(start_response.status_code, 201)
        self.equipment.refresh_from_db()
        self.assertEqual(self.equipment.status, Equipment.STATUS_IN_USE)
        record_id = start_response.data["data"]["id"]
        stop_response = self.client.post(reverse("equipment_usage-stop", args=[record_id]), format="json")
        self.assertEqual(stop_response.status_code, 200)
        self.equipment.refresh_from_db()
        self.assertEqual(self.equipment.status, Equipment.STATUS_IDLE)
        self.assertEqual(EquipmentUsage.objects.filter(equipment=self.equipment).count(), 1)
