from django.utils.html import format_html
from django.contrib import admin
from .models import BodyPart, Equipment, TeamMember, Course, Booking, CheckIn, EquipmentUsage, EquipmentRepair
from common.admin_mixins import ExportExcelMixin

@admin.register(BodyPart)
class BodyPartAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ('name', 'image_preview', 'part', 'status', 'location', 'target_muscles', 'training_focus')
    list_filter = ('part', 'status', 'location')
    search_fields = ('name', 'target_muscles', 'training_focus', 'location')
    actions = ['export_as_excel']
    list_display_links = ('name',)
    list_editable = ('status',)

    @admin.display(description='封面图')
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 4px; object-fit: cover;" />', obj.image.url)
        return "-"

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ('name', 'role', 'phone', 'is_active', 'created_at')
    list_filter = ('role', 'is_active')
    search_fields = ('name', 'phone')
    actions = ['export_as_excel']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ('name', 'coach_display', 'start_time', 'duration', 'booked_count', 'capacity')
    list_filter = ('start_time', 'coach')
    search_fields = ('name',)
    actions = ['export_as_excel']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ('user', 'course', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    actions = ['export_as_excel']
    search_fields = ('user__username', 'course__name')


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ('user', 'method', 'device_id', 'checkin_time', 'checkout_time')
    list_filter = ('method', 'device_id', 'checkin_time')
    search_fields = ('user__username', 'device_id')
    actions = ['export_as_excel']


@admin.register(EquipmentUsage)
class EquipmentUsageAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ('equipment', 'user', 'started_at', 'ended_at', 'duration_minutes')
    list_filter = ('equipment', 'started_at')
    search_fields = ('equipment__name', 'user__username')
    actions = ['export_as_excel']


@admin.register(EquipmentRepair)
class EquipmentRepairAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", "equipment", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("equipment__name", "user__username", "issue_description")
    actions = ["export_as_excel"]
