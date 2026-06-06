from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import serializers, status
from django.utils import timezone
from datetime import date, datetime, time, timedelta
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, inline_serializer
from common.api import ok, fail
from common.demo_content import (
    GYM_CONTENT,
    build_home_content,
    get_course_template,
    get_equipment_template,
    ensure_demo_courses,
    ensure_demo_equipment,
)

class CustomLoginView(LoginView):
    """
    自定义后台登录视图
    """
    template_name = "admin/trae_login.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': '铁馆管理后台登录',
            'site_header': '铁馆管理后台',
            'site_title': '铁馆管理后台',
            'app_path': self.request.get_full_path(),
            # 如果有LOGO配置，可以在这里传
            'logo_url': getattr(settings, 'SIMPLEUI_LOGO', ''),
        })
        return context
    
    def get_success_url(self):
        return '/admin/'


class GymGuideView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="GymGuideEnvelope",
                    fields={
                        "code": serializers.IntegerField(),
                        "message": serializers.CharField(),
                        "data": inline_serializer(
                            name="GymGuideData",
                            fields={
                                "video_url": serializers.CharField(allow_null=True),
                                "cover_image": serializers.CharField(allow_null=True),
                            }
                        ),
                    },
                )
            )
        }
    )
    def get(self, request):
        data = {
            "video_url": "https://wxsnsdy.tc.qq.com/105/20210/snsdyvideodownload?filekey=30280201010421301f0201690402534804102ca905ce620b1241b726bc41dcff44e00204012882540400&bizid=1023&hy=SH&fileparam=302c020101042530230204136ffd93020457e3c4ff02024ef202031e8d7f02030f42400204045a320a0201000400",
            "cover_image": GYM_CONTENT["banner_map"]["store"],
            "duration_seconds": 120,
            "guide_text": "到店后请先完成签到或身份验证，再根据课程安排进入对应训练区域。",
        }
        return ok(data, message="获取成功")


class HomeInfoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="HomeInfoEnvelope",
                    fields={
                        "code": serializers.IntegerField(),
                        "message": serializers.CharField(),
                        "data": serializers.DictField(),
                    },
                )
            )
        }
    )
    def get(self, request):
        from fitness.models import Course, Equipment
        from users.serializers import UserProfileSerializer

        ensure_demo_courses(days=7)
        ensure_demo_equipment()

        now = timezone.now()
        upcoming_courses = (
            Course.objects.select_related("coach")
            .filter(start_time__gte=now)
            .order_by("start_time")[:6]
        )
        course_list = []
        for c in upcoming_courses:
            coach_avatar = None
            coach_title = ""
            course_template = get_course_template(c.name)
            if c.coach_id:
                coach_avatar = getattr(c.coach.avatar, "url", None) if getattr(c.coach, "avatar", None) else None
                coach_title = c.coach.get_role_display()
            course_list.append(
                {
                    "id": c.id,
                    "name": c.name,
                    "start_time": timezone.localtime(c.start_time).strftime("%Y-%m-%d %H:%M:%S"),
                    "duration": c.duration,
                    "coach_name": c.coach_display,
                    "coach_title": coach_title,
                    "coach_avatar": coach_avatar,
                    "capacity": c.capacity,
                    "booked_count": c.booked_count,
                    "category": course_template.get("category", ""),
                    "suitable_for": course_template.get("suitable_for", ""),
                    "intensity_level": course_template.get("intensity_level", ""),
                    "description": course_template.get("description", ""),
                    "class_prep": course_template.get("class_prep", ""),
                    "image_url": course_template.get("image_url", ""),
                }
            )

        equipment_qs = Equipment.objects.select_related("part").all().order_by("id")[:8]
        equipment_list = []
        for e in equipment_qs:
            equipment_template = get_equipment_template(e.name)
            equipment_list.append(
                {
                    "id": e.id,
                    "name": e.name,
                    "description": e.description or equipment_template.get("description", ""),
                    "gif_url": e.gif_url,
                    "part_name": e.part.name if e.part_id else "",
                    "location": e.location,
                    "target_muscles": e.target_muscles or equipment_template.get("target_muscles", ""),
                    "training_focus": getattr(e, "training_focus", "") or equipment_template.get("training_focus", ""),
                    "action_tips": getattr(e, "action_tips", "") or equipment_template.get("action_tips", ""),
                    "precautions": e.precautions or equipment_template.get("precautions", ""),
                    "miniapp_gif_path": getattr(e, "miniapp_gif_path", "") or equipment_template.get("miniapp_gif_path", ""),
                    "image": getattr(e.image, "url", None) if e.image else None,
                }
            )

        user_data = UserProfileSerializer(request.user).data
        data = {
            **build_home_content(),
            "user_status": {
                "nickname": user_data.get("nickname"),
                "balance": user_data.get("balance"),
                "membership_status": user_data.get("membership_status"),
                "days_remaining": user_data.get("days_remaining"),
            },
            "recent_courses": course_list,
            "recommended_equipment": equipment_list,
        }
        return ok(data, message="获取成功")


class CourseScheduleView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="date",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
            )
        ],
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="CourseScheduleEnvelope",
                    fields={
                        "code": serializers.IntegerField(),
                        "message": serializers.CharField(),
                        "data": serializers.DictField(),
                    },
                )
            )
        },
    )
    def get(self, request):
        from fitness.models import Course

        ensure_demo_courses(days=7)

        date_str = (request.query_params.get("date") or "").strip()
        if not date_str:
            return fail("缺少 date", code=400, http_status=400)
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            return fail("date 格式错误", code=400, http_status=400)

        start_dt = timezone.make_aware(datetime.combine(target_date, time.min))
        end_dt = start_dt + timedelta(days=1)
        now = timezone.now()
        query_start_dt = max(start_dt, now) if target_date == timezone.localdate() else start_dt

        courses = (
            Course.objects.select_related("coach")
            .filter(start_time__gte=query_start_dt, start_time__lt=end_dt)
            .order_by("start_time")
        )

        def slot_name(dt):
            h = timezone.localtime(dt).hour
            if 6 <= h < 12:
                return "morning"
            if 12 <= h < 18:
                return "afternoon"
            return "evening"

        slots = {"morning": [], "afternoon": [], "evening": []}
        for c in courses:
            coach_avatar = None
            coach_title = ""
            course_template = get_course_template(c.name)
            if c.coach_id:
                coach_avatar = getattr(c.coach.avatar, "url", None) if getattr(c.coach, "avatar", None) else None
                coach_title = c.coach.get_role_display()
            slots[slot_name(c.start_time)].append(
                {
                    "id": c.id,
                    "name": c.name,
                    "start_time": timezone.localtime(c.start_time).strftime("%H:%M"),
                    "duration": c.duration,
                    "coach_name": c.coach_display,
                    "coach_title": coach_title,
                    "coach_avatar": coach_avatar,
                    "capacity": c.capacity,
                    "booked_count": c.booked_count,
                    "category": course_template.get("category", ""),
                    "suitable_for": course_template.get("suitable_for", ""),
                    "intensity_level": course_template.get("intensity_level", ""),
                    "description": course_template.get("description", ""),
                    "class_prep": course_template.get("class_prep", ""),
                    "image_url": course_template.get("image_url", ""),
                    "membership_hint": course_template.get("membership_hint", ""),
                    "action_type": "book",
                    "action_text": "预约",
                }
            )

        return ok(
            {
                "date": date_str,
                "time_slots": slots,
                "course_categories": build_home_content()["course_categories"],
                "membership_tip": GYM_CONTENT["membership_recommendation"],
            },
            message="获取成功",
        )
