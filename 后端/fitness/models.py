from django.db import models
from django.conf import settings

class BodyPart(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="锻炼部位")

    class Meta:
        verbose_name = "锻炼部位"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Equipment(models.Model):
    STATUS_IDLE = "idle"
    STATUS_IN_USE = "in_use"
    STATUS_MAINTENANCE = "maintenance"
    STATUS_CHOICES = (
        (STATUS_IDLE, "空闲"),
        (STATUS_IN_USE, "使用中"),
        (STATUS_MAINTENANCE, "维修中"),
    )
    name = models.CharField(max_length=100, verbose_name="器械名称")
    part = models.ForeignKey(BodyPart, on_delete=models.CASCADE, verbose_name="锻炼部位", related_name="equipments")
    description = models.TextField(verbose_name="器械描述", blank=True)
    target_muscles = models.CharField(max_length=200, verbose_name="目标肌群", blank=True)
    training_focus = models.CharField(max_length=200, verbose_name="训练定位", blank=True)
    action_tips = models.TextField(verbose_name="动作要点", blank=True)
    precautions = models.TextField(verbose_name="注意事项", blank=True)
    location = models.CharField(max_length=50, verbose_name="位置区域", help_text="如: 有氧区, 力量区")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_IDLE, verbose_name="器械状态")
    gif_url = models.URLField(verbose_name="演示动图URL", blank=True, null=True)
    miniapp_gif_path = models.CharField(max_length=255, verbose_name="小程序动图路径", blank=True)
    image = models.ImageField(upload_to='equipment/', verbose_name="器械图片", blank=True, null=True)

    class Meta:
        verbose_name = "健身器械"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    ROLE_CHOICES = (
        ('coach', '私人教练'),
        ('therapist', '理疗师'),
        ('frontdesk', '前台'),
    )
    name = models.CharField(max_length=100, verbose_name="姓名")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="角色")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="手机号")
    avatar = models.ImageField(upload_to='team/', blank=True, null=True, verbose_name="头像")
    bio = models.TextField(blank=True, verbose_name="简介")
    is_active = models.BooleanField(default=True, verbose_name="在职")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "团队成员"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_role_display()} - {self.name}"

class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name="课程名称")
    coach = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, blank=True, related_name="courses", verbose_name="教练")
    coach_name = models.CharField(max_length=100, verbose_name="教练姓名", blank=True, default="")
    start_time = models.DateTimeField(verbose_name="开始时间")
    duration = models.IntegerField(default=60, verbose_name="时长(分钟)")
    capacity = models.IntegerField(default=20, verbose_name="最大容量")
    booked_count = models.IntegerField(default=0, verbose_name="已预约人数")

    class Meta:
        verbose_name = "课程安排"
        verbose_name_plural = verbose_name
        ordering = ['-start_time']

    def __str__(self): return self.name

    @property
    def coach_display(self):
        if self.coach_id:
            return self.coach.name
        return self.coach_name or "-"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('booked', '已预约'),
        ('cancelled', '已取消'),
        ('completed', '已完成'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked', verbose_name="状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="预约时间")

    class Meta:
        verbose_name = "课程预约"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.name} - {self.user}"


class CheckIn(models.Model):
    METHOD_CHOICES = (
        ("face", "人脸"),
        ("qr", "扫码"),
        ("manual", "人工"),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="manual", verbose_name="方式")
    device_id = models.CharField(max_length=64, blank=True, null=True, verbose_name="设备ID")
    checkin_time = models.DateTimeField(auto_now_add=True, verbose_name="入场时间")
    checkout_time = models.DateTimeField(blank=True, null=True, verbose_name="离场时间")

    class Meta:
        verbose_name = "入场记录"
        verbose_name_plural = verbose_name
        ordering = ["-checkin_time"]

    def __str__(self):
        return f"{self.user} - {self.checkin_time}"


class EquipmentUsage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="用户")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, verbose_name="器械")
    started_at = models.DateTimeField(verbose_name="开始时间")
    ended_at = models.DateTimeField(blank=True, null=True, verbose_name="结束时间")
    duration_minutes = models.IntegerField(default=0, verbose_name="使用时长(分钟)")

    class Meta:
        verbose_name = "器械使用记录"
        verbose_name_plural = verbose_name
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.equipment} - {self.started_at}"


class EquipmentRepair(models.Model):
    STATUS_CHOICES = (
        ("pending", "待处理"),
        ("processing", "处理中"),
        ("resolved", "已完成"),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="equipment_repairs", verbose_name="用户")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="repairs", verbose_name="器械")
    issue_description = models.TextField(verbose_name="问题描述")
    image_url = models.URLField(blank=True, null=True, verbose_name="图片URL")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="提交时间")

    class Meta:
        verbose_name = "器械报修"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
