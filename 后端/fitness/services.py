from typing import List, Optional
from .models import Equipment, BodyPart

class EquipmentService:
    """
    器械业务逻辑层
    """
    
    @staticmethod
    def get_equipment_list(part_id: Optional[int] = None) -> List[Equipment]:
        """
        获取器械列表，支持按部位筛选
        """
        queryset = Equipment.objects.select_related('part').all()
        if part_id:
            queryset = queryset.filter(part_id=part_id)
        return queryset

    @staticmethod
    def get_recommendations(user_profile) -> List[Equipment]:
        """
        根据用户偏好推荐器械 (Mock)
        """
        # 实际逻辑可能涉及查询用户历史记录、身体数据等
        return Equipment.objects.all()[:5]
