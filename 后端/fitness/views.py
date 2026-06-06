from rest_framework import viewsets, status, serializers
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, inline_serializer
from .models import Equipment, TeamMember, Course, Booking, CheckIn, EquipmentUsage, EquipmentRepair
from .serializers import (
    EquipmentSerializer,
    TeamMemberSerializer,
    CourseSerializer,
    BookingSerializer,
    BookingCreateSerializer,
    BookingStatusUpdateSerializer,
    CheckInSerializer,
    CheckInCreateSerializer,
    EquipmentUsageSerializer,
    EquipmentUsageStartSerializer,
    EquipmentUsageStopSerializer,
    EquipmentRepairCreateSerializer,
)
from common.api import ok, fail
from common.demo_content import ensure_demo_equipment

EquipmentListEnvelopeSerializer = inline_serializer(
    name="EquipmentListEnvelope",
    fields={
        "code": serializers.IntegerField(),
        "message": serializers.CharField(),
        "data": EquipmentSerializer(many=True),
    },
)

class EquipmentListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="part_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
            )
        ],
        responses={200: OpenApiResponse(response=EquipmentListEnvelopeSerializer)},
    )
    def get(self, request):
        ensure_demo_equipment()
        part_id = request.query_params.get("part_id")
        status_value = request.query_params.get("status")
        queryset = Equipment.objects.select_related("part").all().order_by("part__name", "name")
        if part_id:
            try:
                part_id_int = int(part_id)
            except (TypeError, ValueError):
                return fail("参数错误", code=400, http_status=400, data={"part_id": "必须为整数"})
            queryset = queryset.filter(part_id=part_id_int)
        if status_value:
            queryset = queryset.filter(status=status_value)
        serializer = EquipmentSerializer(queryset, many=True)
        return ok(serializer.data, message="获取成功")

def equipment_visual_view(request, pk):
    """
    器械可视化详情页 (论文创新模块)
    """
    equipment = get_object_or_404(Equipment, pk=pk)
    # Mock 3D model URL if not exists
    if not hasattr(equipment, 'model_3d_url') or not equipment.model_3d_url:
        equipment.model_3d_url = "/static/models/default.glb"
    
    return render(request, 'equipment_visual.html', {'equipment': equipment})


class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all().order_by("-created_at")
    serializer_class = TeamMemberSerializer

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(role=role)
        active = self.request.query_params.get("active")
        if active is not None:
            if str(active).lower() in {"1", "true", "yes", "y", "on"}:
                qs = qs.filter(is_active=True)
            elif str(active).lower() in {"0", "false", "no", "n", "off"}:
                qs = qs.filter(is_active=False)
        return qs

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


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by("-start_time")
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        upcoming = self.request.query_params.get("upcoming")
        if str(upcoming).lower() in {"1", "true", "yes", "y", "on"}:
            qs = qs.filter(start_time__gte=timezone.now())
        return qs

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


class BookingViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.select_related("course", "user").all().order_by("-created_at")
    serializer_class = BookingSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        serializer = BookingSerializer(self.get_queryset(), many=True)
        return ok(serializer.data, message="获取成功")

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = BookingCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return fail("参数错误", code=400, http_status=400, data=serializer.errors)
        course_id = serializer.validated_data["course_id"]

        try:
            # 预演排他锁：并发扣库存
            course = Course.objects.select_for_update().get(id=course_id)
        except Course.DoesNotExist:
            return fail("课程不存在", code=404, http_status=404)

        if course.start_time <= timezone.now():
            return fail("课程已开始或已结束", code=400, http_status=400)

        if course.booked_count >= course.capacity:
            return fail("课程已满", code=400, http_status=400)

        exists = Booking.objects.filter(user=request.user, course=course, status="booked").exists()
        if exists:
            return fail("已预约该课程", code=400, http_status=400)
            
        booking = Booking.objects.create(user=request.user, course=course, status="booked")
        
        course.booked_count += 1
        course.save(update_fields=["booked_count"])
        
        return ok(BookingSerializer(booking).data, message="预约成功", http_status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def cancel(self, request, pk=None):
        booking = get_object_or_404(Booking, pk=pk)
        if not request.user.is_staff and booking.user_id != request.user.id:
            return fail("无权限", code=403, http_status=403)
        if booking.status != "booked":
            return fail("当前状态不可取消", code=400, http_status=400)

        # 预演排他锁：退款/取消预约时锁定行
        booking = Booking.objects.select_for_update().select_related("course").get(id=booking.id)
        if booking.status != "booked":
            return fail("当前状态不可取消", code=400, http_status=400)
        
        booking.status = "cancelled"
        booking.save(update_fields=["status"])
        
        course = booking.course
        if course.booked_count > 0:
            course.booked_count -= 1
            course.save(update_fields=["booked_count"])

        return ok(BookingSerializer(booking).data, message="取消成功")

    @action(detail=True, methods=["post"])
    def set_status(self, request, pk=None):
        if not request.user.is_staff:
            return fail("无权限", code=403, http_status=403)
        booking = get_object_or_404(Booking, pk=pk)
        serializer = BookingStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return fail("参数错误", code=400, http_status=400, data=serializer.errors)
        new_status = serializer.validated_data["status"]
        if booking.status == new_status:
            return ok(BookingSerializer(booking).data, message="更新成功")

        with transaction.atomic():
            booking = Booking.objects.select_for_update().get(id=booking.id)
            booking.status = new_status
            booking.save(update_fields=["status"])

        return ok(BookingSerializer(booking).data, message="更新成功")


class CheckInViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = CheckIn.objects.select_related("user").all().order_by("-checkin_time")
    serializer_class = CheckInSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        serializer = CheckInSerializer(self.get_queryset(), many=True)
        return ok(serializer.data, message="获取成功")

    @action(detail=False, methods=["post"])
    def checkin(self, request):
        serializer = CheckInCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return fail("参数错误", code=400, http_status=400, data=serializer.errors)
        method = serializer.validated_data.get("method") or "manual"
        open_exists = CheckIn.objects.filter(user=request.user, checkout_time__isnull=True).exists()
        if open_exists:
            return fail("已在馆内", code=400, http_status=400)
        record = CheckIn.objects.create(user=request.user, method=method)
        return ok(CheckInSerializer(record).data, message="入场成功", http_status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        record = CheckIn.objects.filter(user=request.user, checkout_time__isnull=True).order_by("-checkin_time").first()
        if not record:
            return fail("无未完成入场记录", code=400, http_status=400)
        record.checkout_time = timezone.now()
        record.save(update_fields=["checkout_time"])
        return ok(CheckInSerializer(record).data, message="离场成功")


class EquipmentUsageViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EquipmentUsage.objects.select_related("equipment", "user").all().order_by("-started_at")
    serializer_class = EquipmentUsageSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        serializer = EquipmentUsageSerializer(self.get_queryset(), many=True)
        return ok(serializer.data, message="获取成功")

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def start(self, request):
        serializer = EquipmentUsageStartSerializer(data=request.data)
        if not serializer.is_valid():
            return fail("参数错误", code=400, http_status=400, data=serializer.errors)
        equipment_id = serializer.validated_data["equipment_id"]
        started_at = serializer.validated_data.get("started_at") or timezone.now()
        open_exists = EquipmentUsage.objects.filter(user=request.user, ended_at__isnull=True).exists()
        if open_exists:
            return fail("存在未结束的使用记录", code=400, http_status=400)
        equipment = Equipment.objects.select_for_update().filter(pk=equipment_id).first()
        if not equipment:
            return fail("器械不存在", code=404, http_status=404)
        if equipment.status == Equipment.STATUS_MAINTENANCE:
            return fail("当前器械维修中，暂不可使用", code=400, http_status=400)
        equipment_in_use = EquipmentUsage.objects.select_for_update().filter(equipment=equipment, ended_at__isnull=True).exists()
        if equipment_in_use:
            equipment.status = Equipment.STATUS_IN_USE
            equipment.save(update_fields=["status"])
            return fail("当前器械使用中，请稍后再试", code=400, http_status=400)
        record = EquipmentUsage.objects.create(user=request.user, equipment=equipment, started_at=started_at)
        if equipment.status != Equipment.STATUS_IN_USE:
            equipment.status = Equipment.STATUS_IN_USE
            equipment.save(update_fields=["status"])
        return ok(EquipmentUsageSerializer(record).data, message="开始记录成功", http_status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def stop(self, request, pk=None):
        record = EquipmentUsage.objects.select_for_update().select_related("equipment").filter(pk=pk).first()
        if not record:
            return fail("记录不存在", code=404, http_status=404)
        if not request.user.is_staff and record.user_id != request.user.id:
            return fail("无权限", code=403, http_status=403)
        if record.ended_at is not None:
            return fail("记录已结束", code=400, http_status=400)
        serializer = EquipmentUsageStopSerializer(data=request.data)
        if not serializer.is_valid():
            return fail("参数错误", code=400, http_status=400, data=serializer.errors)
        ended_at = serializer.validated_data.get("ended_at") or timezone.now()
        if ended_at <= record.started_at:
            return fail("结束时间不合法", code=400, http_status=400)
        minutes = int((ended_at - record.started_at).total_seconds() // 60)
        record.ended_at = ended_at
        record.duration_minutes = max(minutes, 0)
        record.save(update_fields=["ended_at", "duration_minutes"])
        equipment = Equipment.objects.select_for_update().get(pk=record.equipment_id)
        open_exists = EquipmentUsage.objects.filter(equipment_id=record.equipment_id, ended_at__isnull=True).exclude(pk=record.id).exists()
        if equipment.status == Equipment.STATUS_IN_USE and not open_exists:
            equipment.status = Equipment.STATUS_IDLE
            equipment.save(update_fields=["status"])
        return ok(EquipmentUsageSerializer(record).data, message="结束记录成功")


class EquipmentRepairCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=EquipmentRepairCreateSerializer,
        responses={
            201: OpenApiResponse(
                response=inline_serializer(
                    name="EquipmentRepairCreateEnvelope",
                    fields={
                        "code": serializers.IntegerField(),
                        "message": serializers.CharField(),
                        "data": inline_serializer(
                            name="EquipmentRepairCreateData",
                            fields={"repair_id": serializers.IntegerField()},
                        ),
                    },
                )
            )
        },
    )
    def post(self, request):
        serializer = EquipmentRepairCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return fail("参数错误", code=400, http_status=400, data=serializer.errors)
        equipment_id = serializer.validated_data.get("equipment_id")
        equipment_name = serializer.validated_data.get("equipment_name") or ""
        issue_description = serializer.validated_data["issue_description"]
        image_url = serializer.validated_data.get("image_url") or None

        equipment = None
        if equipment_id:
            equipment = Equipment.objects.filter(id=equipment_id).first()
        if not equipment and equipment_name:
            equipment = Equipment.objects.filter(name=equipment_name).first()
        if not equipment:
            return fail("器械不存在", code=404, http_status=404)

        with transaction.atomic():
            equipment = Equipment.objects.select_for_update().get(pk=equipment.id)
            repair = EquipmentRepair.objects.create(
                user=request.user,
                equipment=equipment,
                issue_description=issue_description,
                image_url=image_url,
                status="pending",
            )
            if equipment.status != Equipment.STATUS_MAINTENANCE:
                equipment.status = Equipment.STATUS_MAINTENANCE
                equipment.save(update_fields=["status"])
        return ok({"repair_id": repair.id}, message="报修成功", http_status=status.HTTP_201_CREATED)
