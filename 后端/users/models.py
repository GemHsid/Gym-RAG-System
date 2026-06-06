from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class UserProfile(AbstractUser):
    openid = models.CharField(max_length=64, unique=True, verbose_name="微信OpenID")
    nickname = models.CharField(max_length=64, verbose_name="昵称")
    avatar = models.URLField(verbose_name="头像URL", blank=True, null=True)
    phone = models.CharField(max_length=11, verbose_name="手机号", blank=True, null=True)
    face_image = models.ImageField(upload_to='faces/', verbose_name="人脸底库", blank=True, null=True)
    is_face_verified = models.BooleanField(default=False, verbose_name="是否已录入人脸")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="余额")
    membership_expiry = models.DateField(null=True, blank=True, verbose_name="会员到期日")

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedbacks", verbose_name="用户")
    content = models.TextField(verbose_name="内容")
    image = models.ImageField(upload_to="feedback/", blank=True, null=True, verbose_name="图片")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="提交时间")

    class Meta:
        verbose_name = "意见反馈"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
