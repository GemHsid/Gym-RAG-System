from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WechatLoginView, UserProfileView, TokenRefreshWrappedView, UserMeView, FaceRegisterView, FaceVerifyView, VisitHistoryView, FeedbackCreateView, MemberAdminViewSet

router = DefaultRouter()
router.register(r"members", MemberAdminViewSet, basename="members")

urlpatterns = [
    path('login/', WechatLoginView.as_view(), name='wechat_login'),
    path('me/', UserMeView.as_view(), name='me'),
    path('profile/', UserProfileView.as_view(), name='user_profile_current'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name='user_profile'),
    path('face/register/', FaceRegisterView.as_view(), name='face_register'),
    path('face/verify/', FaceVerifyView.as_view(), name='face_verify'),
    path('visit-history/', VisitHistoryView.as_view(), name='visit_history'),
    path('feedback/', FeedbackCreateView.as_view(), name='feedback'),
    path("token/refresh/", TokenRefreshWrappedView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]
