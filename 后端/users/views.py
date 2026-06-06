from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, inline_serializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.utils import timezone
from .models import UserProfile, Feedback
from .serializers import UserProfileSerializer, UserMeUpdateSerializer, AdminUserProfileSerializer
from common.api import ok, fail
from common.demo_content import build_profile_content
import base64
import json
import logging
import os
import time
import urllib.parse
import urllib.request

_baidu_access_token = None
_baidu_access_token_expire_at = 0
logger = logging.getLogger(__name__)


def _baidu_get_access_token():
    global _baidu_access_token, _baidu_access_token_expire_at
    config = getattr(settings, "BAIDU_AI_CONFIG", {}) or {}
    api_key = (config.get("API_KEY") or "").strip()
    secret_key = (config.get("SECRET_KEY") or "").strip()
    if not api_key or not secret_key:
        return None
    now = time.time()
    if _baidu_access_token and now < (_baidu_access_token_expire_at - 60):
        return _baidu_access_token
    token_url = "https://aip.baidubce.com/oauth/2.0/token"
    form = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": api_key,
            "client_secret": secret_key,
        }
    ).encode("utf-8")
    req = urllib.request.Request(token_url, data=form, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None
    token = payload.get("access_token")
    expires_in = payload.get("expires_in") or 0
    if not token:
        return None
    _baidu_access_token = token
    _baidu_access_token_expire_at = now + int(expires_in or 0)
    return token


def _file_to_base64(uploaded_file):
    if not uploaded_file:
        return None
    content = uploaded_file.read()
    if not content:
        return None
    return base64.b64encode(content).decode("utf-8")


def _fieldfile_to_base64(field_file):
    if not field_file:
        return None
    try:
        field_file.open("rb")
        content = field_file.read()
    except Exception:
        return None
    finally:
        try:
            field_file.close()
        except Exception:
            pass
    if not content:
        return None
    return base64.b64encode(content).decode("utf-8")

import requests

class WechatLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=inline_serializer(
            name="WechatLoginRequest",
            fields={"code": serializers.CharField()},
        ),
        responses=inline_serializer(
            name="WechatLoginEnvelope",
            fields={
                "code": serializers.IntegerField(),
                "message": serializers.CharField(),
                "data": inline_serializer(
                    name="WechatLoginData",
                    fields={
                        "access": serializers.CharField(),
                        "refresh": serializers.CharField(),
                        "user_id": serializers.IntegerField(),
                        "is_new": serializers.BooleanField(),
                        "nickname": serializers.CharField(),
                    },
                ),
            },
        ),
    )
    def post(self, request):
        code = request.data.get('code')
        if not code:
            return fail("缺少微信登录 code", code=400, http_status=400)

        # 1. 从环境变量获取微信小程序配置
        appid = os.environ.get("WECHAT_APPID", "")
        secret = os.environ.get("WECHAT_SECRET", "")
        
        if not appid or not secret:
            # 如果没有配置环境变量，降级为 Mock 逻辑，保证开发环境不阻塞
            openid = f'mock_openid_{code[:5]}'
        else:
            # 2. 调用微信官方接口换取 OpenID
            url = "https://api.weixin.qq.com/sns/jscode2session"
            params = {
                "appid": appid,
                "secret": secret,
                "js_code": code,
                "grant_type": "authorization_code"
            }
            try:
                resp = requests.get(url, params=params, timeout=5)
                data = resp.json()
                
                # 处理微信返回的错误
                if "errcode" in data and data["errcode"] != 0:
                    return fail(f"微信登录失败: {data.get('errmsg')}", code=401, http_status=401)
                
                openid = data.get("openid")
                session_key = data.get("session_key") # 后续如需解密手机号可保存此 key
                
                if not openid:
                    return fail("未能获取到 OpenID", code=401, http_status=401)
            except Exception as e:
                return fail(f"请求微信接口异常: {str(e)}", code=502, http_status=502)
        
        # 3. 查找或静默创建用户
        user, created = UserProfile.objects.get_or_create(username=openid, defaults={
            'openid': openid,
            'nickname': '微信用户',
            'balance': 0
        })
        
        # 为了适配之前的逻辑，确保 wechat_openid 字段有值（假设模型中已定义或使用 openid 字段）
        # 这里我们的 UserProfile 模型使用的是 openid 作为唯一标识
        
        # 4. 手动生成 SimpleJWT
        refresh = RefreshToken.for_user(user)

        return ok(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_id": user.id,
                "is_new": created,
                "nickname": user.nickname,
            },
            message="登录成功",
        )

@extend_schema_view(
    get=extend_schema(
        responses=inline_serializer(
            name="UserProfileEnvelope",
            fields={
                "code": serializers.IntegerField(),
                "message": serializers.CharField(),
                "data": UserProfileSerializer(),
            },
        )
    )
)
class UserProfileView(RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        data.update(build_profile_content())
        return ok(data, message="获取成功")


class TokenRefreshWrappedView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code >= 400:
            return ok(None, message="刷新失败", code=response.status_code, http_status=response.status_code)
        return ok(response.data, message="刷新成功", http_status=response.status_code)


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=inline_serializer(
            name="UserMeGetEnvelope",
            fields={
                "code": serializers.IntegerField(),
                "message": serializers.CharField(),
                "data": UserProfileSerializer(),
            },
        )
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        data = serializer.data
        data.update(build_profile_content())
        return ok(data, message="获取成功")

    @extend_schema(
        request=UserMeUpdateSerializer,
        responses=inline_serializer(
            name="UserMePatchEnvelope",
            fields={
                "code": serializers.IntegerField(),
                "message": serializers.CharField(),
                "data": UserProfileSerializer(),
            },
        ),
    )
    def patch(self, request):
        serializer = UserMeUpdateSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return fail("参数错误", code=400, http_status=400, data=serializer.errors)
        serializer.save()
        return ok(UserProfileSerializer(request.user).data, message="更新成功")


class FaceRegisterView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        request=inline_serializer(
            name="FaceRegisterRequest",
            fields={"face_image": serializers.FileField()},
        ),
        responses=inline_serializer(
            name="FaceRegisterEnvelope",
            fields={
                "code": serializers.IntegerField(),
                "message": serializers.CharField(),
                "data": inline_serializer(
                    name="FaceRegisterData",
                    fields={
                        "face_image": serializers.CharField(allow_null=True),
                        "is_face_verified": serializers.BooleanField(),
                    },
                ),
            },
        ),
    )
    def post(self, request):
        user = request.user
        face_image = request.FILES.get("face_image")
        if not face_image:
            return fail("缺少 face_image", code=400, http_status=400)
        user.face_image = face_image
        user.is_face_verified = True
        user.save(update_fields=["face_image", "is_face_verified"])
        return ok(UserProfileSerializer(user).data, message="录入成功", http_status=status.HTTP_201_CREATED)


class FaceVerifyView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        request=inline_serializer(
            name="FaceVerifyRequest",
            fields={
                "face_image": serializers.FileField(),
                "device_id": serializers.CharField(required=False, allow_blank=True),
            },
        ),
        responses=inline_serializer(
            name="FaceVerifyEnvelope",
            fields={
                "code": serializers.IntegerField(),
                "message": serializers.CharField(),
                "data": inline_serializer(
                    name="FaceVerifyData",
                    fields={
                        "passed": serializers.BooleanField(),
                        "similarity": serializers.FloatField(),
                        "action": serializers.CharField(),
                        "checkin_id": serializers.IntegerField(allow_null=True),
                    },
                ),
            },
        ),
    )
    def post(self, request):
        user = request.user
        face_image = request.FILES.get("face_image")
        device_id = request.data.get("device_id") or ""
        
        if not face_image:
            return fail("缺少 face_image", code=400, http_status=400)
        if not getattr(user, "is_face_verified", False) or not getattr(user, "face_image", None):
            return fail("未录入人脸，请先完成人脸录入", code=400, http_status=400)

        live_b64 = _file_to_base64(face_image)
        registered_b64 = _fieldfile_to_base64(user.face_image)
        if not live_b64 or not registered_b64:
            return fail("人脸图片读取失败", code=400, http_status=400)

        token = _baidu_get_access_token()
        if not token:
            return fail("人脸识别未配置（缺少 BAIDU_API_KEY/BAIDU_SECRET_KEY）", code=501, http_status=501)

        similarity = 0.0
        threshold = float(getattr(settings, "FACE_VERIFY_SCORE_THRESHOLD", 80.0) or 80.0)
        url = f"https://aip.baidubce.com/rest/2.0/face/v3/match?access_token={urllib.parse.quote(token)}"
        body = json.dumps(
            [
                {
                    "image": live_b64,
                    "image_type": "BASE64",
                    "face_type": "LIVE",
                    "quality_control": "NORMAL",
                    "liveness_control": "NORMAL",
                },
                {
                    "image": registered_b64,
                    "image_type": "BASE64",
                    "face_type": "LIVE",
                    "quality_control": "LOW",
                    "liveness_control": "LOW",
                },
            ]
        ).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            logger.error("百度人脸识别请求失败: %s", exc)
            payload = None
        if not payload or payload.get("error_code") not in (0, "0"):
            msg = "人脸识别服务异常"
            if payload and payload.get("error_msg"):
                msg = payload.get("error_msg")
            logger.error("百度人脸识别响应异常: %s", payload)
            return fail(msg, code=502, http_status=502)
        result = payload.get("result") or {}
        similarity = float(result.get("score") or 0)

        passed = similarity >= threshold
        if not passed:
            return ok(
                {"passed": False, "similarity": similarity, "action": "none", "checkin_id": None},
                message="验证完成",
            )

        from fitness.models import CheckIn

        active = (
            CheckIn.objects.filter(user=user, checkout_time__isnull=True)
            .order_by("-checkin_time")
            .first()
        )
        if active:
            active.checkout_time = timezone.now()
            active.save(update_fields=["checkout_time"])
            return ok(
                {
                    "passed": True,
                    "similarity": similarity,
                    "action": "checkout",
                    "checkin_id": active.id,
                },
                message="验证完成",
            )

        record = CheckIn.objects.create(user=user, method="face", device_id=device_id)
        return ok(
            {
                "passed": True,
                "similarity": similarity,
                "action": "checkin",
                "checkin_id": record.id,
            },
            message="验证完成",
        )


class VisitHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=inline_serializer(
            name="VisitHistoryEnvelope",
            fields={
                "code": serializers.IntegerField(),
                "message": serializers.CharField(),
                "data": inline_serializer(
                    name="VisitHistoryList",
                    fields={
                        "id": serializers.IntegerField(),
                        "visit_time": serializers.CharField(),
                        "method": serializers.CharField(),
                        "duration_minutes": serializers.IntegerField(),
                    },
                    many=True,
                ),
            },
        )
    )
    def get(self, request):
        from fitness.models import CheckIn

        def format_method(value: str):
            mapping = {"face": "人脸识别", "qr": "扫码", "manual": "人工"}
            return mapping.get(value, "未知")

        records = CheckIn.objects.filter(user=request.user).order_by("-checkin_time")[:50]
        data = []
        for r in records:
            checkin_time = timezone.localtime(r.checkin_time)
            minutes = 0
            if r.checkout_time:
                delta = timezone.localtime(r.checkout_time) - checkin_time
                minutes = max(int(delta.total_seconds() // 60), 0)
            data.append(
                {
                    "id": r.id,
                    "visit_time": checkin_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "method": format_method(r.method),
                    "duration_minutes": minutes,
                }
            )
        return ok(data, message="获取成功")


class FeedbackCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        request=inline_serializer(
            name="FeedbackCreateRequest",
            fields={
                "content": serializers.CharField(),
                "image": serializers.FileField(required=False),
            },
        ),
        responses=inline_serializer(
            name="FeedbackCreateEnvelope",
            fields={
                "code": serializers.IntegerField(),
                "message": serializers.CharField(),
                "data": serializers.JSONField(allow_null=True),
            },
        ),
    )
    def post(self, request):
        content = (request.data.get("content") or "").strip()
        if not content:
            return fail("缺少 content", code=400, http_status=400)
        image = request.FILES.get("image")
        Feedback.objects.create(user=request.user, content=content, image=image)
        return ok(None, message="提交成功", http_status=status.HTTP_201_CREATED)


class MemberAdminViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all().order_by("-id")
    serializer_class = AdminUserProfileSerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return ok(response.data, message="获取成功", http_status=response.status_code)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return ok(response.data, message="获取成功", http_status=response.status_code)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return ok(response.data, message="创建成功", http_status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return ok(response.data, message="更新成功", http_status=response.status_code)

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return ok(response.data, message="更新成功", http_status=response.status_code)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return ok(None, message="删除成功", http_status=status.HTTP_204_NO_CONTENT)
