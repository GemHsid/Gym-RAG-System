from rest_framework import serializers
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field, inline_serializer
from .models import UserProfile
from datetime import date

class UserProfileSerializer(serializers.ModelSerializer):
    days_remaining = serializers.SerializerMethodField()
    membership_status = serializers.SerializerMethodField()
    total_training_days = serializers.SerializerMethodField()
    total_training_count = serializers.SerializerMethodField()
    monthly_stats = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'nickname',
            'avatar',
            'phone',
            'balance',
            'membership_expiry',
            'days_remaining',
            'membership_status',
            'total_training_days',
            'total_training_count',
            'is_face_verified',
            'face_image',
            'monthly_stats',
        ]

    @extend_schema_field(serializers.IntegerField())
    def get_days_remaining(self, obj):
        if obj.membership_expiry:
            delta = obj.membership_expiry - date.today()
            return max(delta.days, 0)
        return 0

    @extend_schema_field(serializers.CharField())
    def get_membership_status(self, obj):
        if not obj.membership_expiry:
            return "none"
        if obj.membership_expiry >= date.today():
            return "active"
        return "expired"

    @extend_schema_field(serializers.IntegerField())
    def get_total_training_count(self, obj):
        from fitness.models import CheckIn

        return CheckIn.objects.filter(user=obj).count()

    @extend_schema_field(serializers.IntegerField())
    def get_total_training_days(self, obj):
        from fitness.models import CheckIn, EquipmentUsage

        checkin_dates = set()
        for dt in CheckIn.objects.filter(user=obj).values_list("checkin_time", flat=True).iterator():
            if dt:
                checkin_dates.add(timezone.localdate(dt))

        usage_dates = set()
        for dt in EquipmentUsage.objects.filter(user=obj).values_list("started_at", flat=True).iterator():
            if dt:
                usage_dates.add(timezone.localdate(dt))

        return len(checkin_dates | usage_dates)

    @extend_schema_field(
        inline_serializer(
            name="UserMonthlyStats",
            fields={
                "count": serializers.IntegerField(),
                "days": serializers.IntegerField(),
                "duration": serializers.IntegerField(),
            },
        )
    )
    def get_monthly_stats(self, obj):
        from fitness.models import CheckIn, EquipmentUsage

        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)

        checkins = (
            CheckIn.objects.filter(user=obj, checkin_time__gte=month_start, checkin_time__lt=month_end)
            .only("checkin_time", "checkout_time")
            .order_by("-checkin_time")
        )
        monthly_count = checkins.count()

        day_set = set()
        duration_minutes = 0
        for r in checkins.iterator():
            if r.checkin_time:
                day_set.add(timezone.localdate(r.checkin_time))
            if r.checkout_time and r.checkin_time:
                delta = timezone.localtime(r.checkout_time) - timezone.localtime(r.checkin_time)
                duration_minutes += max(int(delta.total_seconds() // 60), 0)

        usage_duration = (
            EquipmentUsage.objects.filter(user=obj, started_at__gte=month_start, started_at__lt=month_end)
            .values_list("duration_minutes", flat=True)
        )
        usage_sum = sum([int(v or 0) for v in usage_duration])
        if usage_sum > 0:
            duration_minutes = usage_sum

        return {"count": monthly_count, "days": len(day_set), "duration": int(duration_minutes)}


class UserMeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['nickname', 'avatar', 'phone']


class AdminUserProfileSerializer(serializers.ModelSerializer):
    days_remaining = serializers.SerializerMethodField()
    membership_status = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'username',
            'openid',
            'nickname',
            'avatar',
            'phone',
            'is_active',
            'is_staff',
            'balance',
            'membership_expiry',
            'days_remaining',
            'membership_status',
            'is_face_verified',
            'face_image',
            'date_joined',
            'last_login',
        ]
        read_only_fields = ['date_joined', 'last_login']

    @extend_schema_field(serializers.IntegerField())
    def get_days_remaining(self, obj):
        if obj.membership_expiry:
            delta = obj.membership_expiry - date.today()
            return max(delta.days, 0)
        return 0

    @extend_schema_field(serializers.CharField())
    def get_membership_status(self, obj):
        if not obj.membership_expiry:
            return "none"
        if obj.membership_expiry >= date.today():
            return "active"
        return "expired"
