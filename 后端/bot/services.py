class BotService:
    @staticmethod
    def detect_intent(message):
        """简单的关键词意图识别"""
        if "练胸" in message or "怎么练" in message or "深蹲" in message:
            return "TRAINING_GUIDE"
        elif "多少钱" in message or "价格" in message or "会员" in message:
            return "PRICING"
        elif "蝴蝶机" in message or "器材" in message:
            return "EQUIPMENT_INFO"
        return "CHIT_CHAT"
