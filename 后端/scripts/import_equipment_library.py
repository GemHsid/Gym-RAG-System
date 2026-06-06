import json
import os
import sys

import django
from django.core.files import File


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, BASE_DIR)
django.setup()

from fitness.models import BodyPart, Equipment


def normalize_status(value):
    raw = str(value or "").strip().lower()
    mapping = {
        "idle": Equipment.STATUS_IDLE,
        "空闲": Equipment.STATUS_IDLE,
        "in_use": Equipment.STATUS_IN_USE,
        "使用中": Equipment.STATUS_IN_USE,
        "maintenance": Equipment.STATUS_MAINTENANCE,
        "维修中": Equipment.STATUS_MAINTENANCE,
    }
    return mapping.get(raw, Equipment.STATUS_IDLE)


def resolve_image_path(base_path, image_path):
    if not image_path:
        return ""
    if os.path.isabs(image_path):
        return image_path
    return os.path.abspath(os.path.join(base_path, image_path))


def bind_image_file(equipment, image_path):
    full_path = resolve_image_path(BASE_DIR, image_path)
    if not full_path or not os.path.exists(full_path):
        return False
    with open(full_path, "rb") as image_file:
        equipment.image.save(os.path.basename(full_path), File(image_file), save=False)
    return True


def upsert_equipment(item):
    name = str(item.get("name") or "").strip()
    part_name = str(item.get("part_name") or item.get("part") or "").strip()
    location = str(item.get("location") or "").strip()
    if not name or not part_name or not location:
        raise ValueError(f"器械数据缺少必填项: {item}")
    part, _ = BodyPart.objects.get_or_create(name=part_name)
    equipment, created = Equipment.objects.get_or_create(name=name, defaults={"part": part, "location": location})
    equipment.part = part
    equipment.location = location
    equipment.description = str(item.get("description") or "").strip()
    equipment.target_muscles = str(item.get("target_muscles") or "").strip()
    equipment.precautions = str(item.get("precautions") or "").strip()
    equipment.gif_url = str(item.get("gif_url") or "").strip() or None
    equipment.status = normalize_status(item.get("status"))
    image_path = str(item.get("image_path") or "").strip()
    if image_path:
        bind_image_file(equipment, image_path)
    equipment.save()
    return equipment, created


def main():
    source_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE_DIR, "scripts", "equipment_library.template.json")
    source_path = os.path.abspath(source_path)
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"未找到数据文件: {source_path}")
    with open(source_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    items = payload.get("items") if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        raise ValueError("JSON 结构错误，必须是数组或 {\"items\": [...]} 格式")
    created_count = 0
    updated_count = 0
    for item in items:
        _, created = upsert_equipment(item)
        if created:
            created_count += 1
        else:
            updated_count += 1
    print(f"导入完成：新增 {created_count} 条，更新 {updated_count} 条")


if __name__ == "__main__":
    main()
