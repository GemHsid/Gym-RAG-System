from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquipmentListView, equipment_visual_view, TeamMemberViewSet, CourseViewSet, BookingViewSet, CheckInViewSet, EquipmentUsageViewSet

router = DefaultRouter()
router.register(r"team", TeamMemberViewSet, basename="team")
router.register(r"courses", CourseViewSet, basename="courses")
router.register(r"bookings", BookingViewSet, basename="bookings")
router.register(r"checkins", CheckInViewSet, basename="checkins")
router.register(r"equipment-usage", EquipmentUsageViewSet, basename="equipment_usage")

urlpatterns = [
    path('equipment/', EquipmentListView.as_view(), name='equipment_list'),
    path('visual/<int:pk>/', equipment_visual_view, name='equipment_visual'),
    path("", include(router.urls)),
]
