import os
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from bot.models import ChatMessage
from fitness.models import Booking, Course
from orders.models import MembershipProduct, Order
from users.models import UserProfile


class IntegrationFlowTests(APITestCase):
    def setUp(self):
        """
        集成测试公共初始化：
        - 为每个 test 方法准备一套独立的数据库初始数据
        - 提供创建用户、生成 JWT、设置 Authorization Header 的通用方法
        """
        self.login_url = "/api/users/login/"
        self.me_url = "/api/users/me/"
        self.purchase_url = "/api/orders/purchase/"
        self.booking_url = "/api/fitness/bookings/"
        self.bot_chat_url = "/api/bot/chat/"

    def _create_user(self, *, username: str, openid: str, nickname: str, balance: Decimal = Decimal("0.00")):
        """
        创建业务用户（AUTH_USER_MODEL = users.UserProfile）。
        """
        return UserProfile.objects.create_user(
            username=username,
            password="test_password_123",
            openid=openid,
            nickname=nickname,
            balance=balance,
        )

    def _issue_access_token(self, user: UserProfile) -> str:
        """
        直接用 SimpleJWT 为指定用户生成 access token（不走登录接口）。
        """
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def _auth(self, token: str):
        """
        设置鉴权 Header（和契约保持一致：Authorization: Bearer <access>）。
        """
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

    def _unauth(self):
        """
        清空鉴权 Header，用于测试 401。
        """
        self.client.credentials()

    def test_auth_get_token_via_wechat_login_mock(self):
        """
        [User & Auth] 测试正常获取 Token（Mock 微信登录请求）：
        - 调用 POST /api/users/login/
        - 断言返回结构包含 access/refresh/user_id/is_new/nickname
        """
        payload = {"code": "wx.login_mock_code"}
        resp = self.client.post(self.login_url, payload, format="json")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["code"], 0)
        self.assertEqual(resp.data["message"], "登录成功")

        data = resp.data["data"]
        self.assertEqual("access" in data, True)
        self.assertEqual("refresh" in data, True)
        self.assertEqual("user_id" in data, True)
        self.assertEqual("is_new" in data, True)
        self.assertEqual("nickname" in data, True)

    def test_auth_me_with_token_returns_profile_fields(self):
        """
        [User & Auth] 测试使用 Token 访问 /api/users/me/ 获取个人资料：
        - 先调用登录接口拿到 access token
        - 携带 Authorization: Bearer <token> 请求 /api/users/me/
        - 断言 data 包含 nickname、balance 等字段
        """
        login_resp = self.client.post(self.login_url, {"code": "any"}, format="json")
        self.assertEqual(login_resp.status_code, 200)
        token = login_resp.data["data"]["access"]

        self._auth(token)
        me_resp = self.client.get(self.me_url)

        self.assertEqual(me_resp.status_code, 200)
        self.assertEqual(me_resp.data["code"], 0)

        profile = me_resp.data["data"]
        self.assertEqual("nickname" in profile, True)
        self.assertEqual("balance" in profile, True)

    def test_auth_protected_endpoint_without_token_returns_401(self):
        """
        [User & Auth] 测试无 Token 访问受保护接口，断言返回 401 Unauthorized：
        - 不设置 Authorization Header
        - 访问 /api/users/me/
        """
        self._unauth()
        resp = self.client.get(self.me_url)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.data["code"], 401)

    def test_orders_purchase_success_deducts_balance_and_extends_membership(self):
        """
        [Orders] 测试【正常购买】：
        - 初始化用户余额 500
        - 初始化会员卡产品售价 300、有效期 days_duration
        - POST /api/orders/purchase/
        - 断言扣款后余额正确、订单生成、会员到期日延后
        """
        user = self._create_user(
            username="buyer_success",
            openid="openid_buyer_success",
            nickname="购买用户",
            balance=Decimal("500.00"),
        )
        token = self._issue_access_token(user)
        self._auth(token)

        product = MembershipProduct.objects.create(
            name="测试会员卡",
            price=Decimal("300.00"),
            original_price=Decimal("300.00"),
            tags=[],
            is_promotion=False,
            days_duration=30,
        )

        before_balance = user.balance
        before_expiry = user.membership_expiry

        resp = self.client.post(self.purchase_url, {"product_id": product.id}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["code"], 0)

        user.refresh_from_db()
        self.assertEqual(user.balance, Decimal("200.00"))
        self.assertEqual(user.balance, before_balance - product.price)

        order_count = Order.objects.filter(user=user, product=product).count()
        self.assertEqual(order_count, 1)

        today = date.today()
        if before_expiry and before_expiry >= today:
            expected_expiry = before_expiry + timedelta(days=product.days_duration)
        else:
            expected_expiry = today + timedelta(days=product.days_duration)
        self.assertEqual(user.membership_expiry, expected_expiry)

    def test_orders_purchase_insufficient_balance_returns_400(self):
        """
        [Orders] 测试【异常边界 - 余额不足】：
        - 初始化用户余额 500
        - 初始化产品价格 1000
        - 提交购买请求
        - 断言返回 400，且用户余额未变化，且不产生订单
        """
        user = self._create_user(
            username="buyer_fail",
            openid="openid_buyer_fail",
            nickname="购买失败用户",
            balance=Decimal("500.00"),
        )
        token = self._issue_access_token(user)
        self._auth(token)

        product = MembershipProduct.objects.create(
            name="测试高价会员卡",
            price=Decimal("1000.00"),
            original_price=Decimal("1000.00"),
            tags=[],
            is_promotion=False,
            days_duration=30,
        )

        before_balance = user.balance
        resp = self.client.post(self.purchase_url, {"product_id": product.id}, format="json")

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["code"], 400)

        user.refresh_from_db()
        self.assertEqual(user.balance, before_balance)
        self.assertEqual(Order.objects.filter(user=user).count(), 0)

    def test_fitness_booking_prevent_oversell(self):
        """
        [Fitness] 测试健身业务防超卖：
        - 初始化课程 capacity=1 且 start_time 在未来
        - 用户 A 预约成功（201）
        - 用户 B 紧接着预约同一课程，返回 400（课程已满）
        - 断言数据库 Booking 记录只有 1 条
        """
        course = Course.objects.create(
            name="测试课程",
            coach=None,
            coach_name="测试教练",
            start_time=timezone.now() + timedelta(days=1),
            duration=60,
            capacity=1,
            booked_count=0,
        )

        user_a = self._create_user(
            username="user_a",
            openid="openid_user_a",
            nickname="用户A",
            balance=Decimal("0.00"),
        )
        token_a = self._issue_access_token(user_a)
        self._auth(token_a)

        resp_a = self.client.post(self.booking_url, {"course_id": course.id}, format="json")
        self.assertEqual(resp_a.status_code, 201)
        self.assertEqual(resp_a.data["code"], 0)

        user_b = self._create_user(
            username="user_b",
            openid="openid_user_b",
            nickname="用户B",
            balance=Decimal("0.00"),
        )
        token_b = self._issue_access_token(user_b)
        self._auth(token_b)

        resp_b = self.client.post(self.booking_url, {"course_id": course.id}, format="json")
        self.assertEqual(resp_b.status_code, 400)
        self.assertEqual(resp_b.data["code"], 400)

        self.assertEqual(Booking.objects.filter(course=course).count(), 1)
        course.refresh_from_db()
        self.assertEqual(course.booked_count, 1)

    @patch("bot.views.OpenAI")
    def test_bot_chat_mock_llm_and_persist_chatmessage(self, mock_openai):
        """
        [Bot] 测试 AI 助手连通性：
        - Mock 外部大模型请求（不真的请求网络）
        - POST /api/bot/chat/ 发送消息
        - 断言响应包含 AI 回复
        - 断言数据库创建了 ChatMessage（user + ai 两条）
        """
        os.environ["MOLIFANGZHOU_API_KEY"] = "fake_key_for_test"

        user = self._create_user(
            username="chat_user",
            openid="openid_chat_user",
            nickname="对话用户",
            balance=Decimal("0.00"),
        )
        token = self._issue_access_token(user)
        self._auth(token)

        preset_answer = "这是一个预设的 AI 回复"

        class _DummyChoiceMessage:
            def __init__(self, content: str):
                self.content = content

        class _DummyChoice:
            def __init__(self, content: str):
                self.message = _DummyChoiceMessage(content)

        class _DummyResponse:
            def __init__(self, content: str):
                self.choices = [_DummyChoice(content)]

        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.return_value = _DummyResponse(preset_answer)

        before_count = ChatMessage.objects.filter(session__user=user).count()
        resp = self.client.post(self.bot_chat_url, {"message": "怎么练胸？"}, format="json")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["code"], 0)
        self.assertEqual(resp.data["data"]["answer"], preset_answer)

        after_count = ChatMessage.objects.filter(session__user=user).count()
        self.assertEqual(after_count, before_count + 2)
        self.assertEqual(
            ChatMessage.objects.filter(session__user=user, role="ai", content=preset_answer).exists(),
            True,
        )


# 一行命令运行本文件全部集成测试：
# python manage.py test tests_integration -v 2
