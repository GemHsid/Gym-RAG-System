from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import BodyPart, Equipment, TeamMember, Course, Booking, CheckIn, EquipmentUsage
from common.demo_content import get_course_template

class BodyPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyPart
        fields = ['id', 'name']

class EquipmentSerializer(serializers.ModelSerializer):
    part_id = serializers.IntegerField(source='part.id', read_only=True)
    part_name = serializers.CharField(source='part.name', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Equipment
        fields = [
            'id',
            'name',
            'description',
            'target_muscles',
            'training_focus',
            'action_tips',
            'precautions',
            'gif_url',
            'miniapp_gif_path',
            'part_id',
            'part_name',
            'location',
            'status',
            'status_label',
            'image',
        ]


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['id', 'name', 'role', 'phone', 'avatar', 'bio', 'is_active']


class CourseSerializer(serializers.ModelSerializer):
    coach_display = serializers.CharField(read_only=True)
    available_seats = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    suitable_for = serializers.SerializerMethodField()
    intensity_level = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    class_prep = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    membership_hint = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'name',
            'coach',
            'coach_name',
            'coach_display',
            'start_time',
            'duration',
            'capacity',
            'booked_count',
            'available_seats',
            'category',
            'suitable_for',
            'intensity_level',
            'description',
            'class_prep',
            'image_url',
            'membership_hint',
        ]

    @extend_schema_field(serializers.IntegerField())
    def get_available_seats(self, obj):
        return max(obj.capacity - obj.booked_count, 0)

    def _get_template_value(self, obj, key):
        return get_course_template(obj.name).get(key, "")

    @extend_schema_field(serializers.CharField())
    def get_category(self, obj):
        return self._get_template_value(obj, "category")

    @extend_schema_field(serializers.CharField())
    def get_suitable_for(self, obj):
        return self._get_template_value(obj, "suitable_for")

    @extend_schema_field(serializers.CharField())
    def get_intensity_level(self, obj):
        return self._get_template_value(obj, "intensity_level")

    @extend_schema_field(serializers.CharField())
    def get_description(self, obj):
        return self._get_template_value(obj, "description")

    @extend_schema_field(serializers.CharField())
    def get_class_prep(self, obj):
        return self._get_template_value(obj, "class_prep")

    @extend_schema_field(serializers.CharField())
    def get_image_url(self, obj):
        return self._get_template_value(obj, "image_url")

    @extend_schema_field(serializers.CharField())
    def get_membership_hint(self, obj):
        return self._get_template_value(obj, "membership_hint")


class BookingSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'course', 'status', 'created_at']


class BookingCreateSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()


class BookingStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[c[0] for c in Booking.STATUS_CHOICES])


class CheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckIn
        fields = ['id', 'method', 'checkin_time', 'checkout_time']


class CheckInCreateSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=[c[0] for c in CheckIn.METHOD_CHOICES], required=False)


class EquipmentUsageSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)

    class Meta:
        model = EquipmentUsage
        fields = ['id', 'equipment', 'equipment_name', 'started_at', 'ended_at', 'duration_minutes']


class EquipmentUsageStartSerializer(serializers.Serializer):
    equipment_id = serializers.IntegerField()
    started_at = serializers.DateTimeField(required=False)


class EquipmentUsageStopSerializer(serializers.Serializer):
    ended_at = serializers.DateTimeField(required=False)


class EquipmentRepairCreateSerializer(serializers.Serializer):
    equipment_id = serializers.IntegerField(required=False)
    equipment_name = serializers.CharField(required=False, allow_blank=True)
    issue_description = serializers.CharField()
    image_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)

    def validate(self, attrs):
        equipment_id = attrs.get("equipment_id")
        equipment_name = (attrs.get("equipment_name") or "").strip()
        if not equipment_id and not equipment_name:
            raise serializers.ValidationError("equipment_id 或 equipment_name 至少传一个")
        if equipment_name:
            attrs["equipment_name"] = equipment_name
        return attrs
