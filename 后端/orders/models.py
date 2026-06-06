from django.db import models
from django.conf import settings

class MembershipProduct(models.Model):
    name = models.CharField(max_length=100, verbose_name="产品名称")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    original_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="原价", blank=True, null=True)
    tags = models.JSONField(default=list, blank=True, verbose_name="标签")
    is_promotion = models.BooleanField(default=False, verbose_name="是否促销")
    days_duration = models.IntegerField(help_text="会员有效期天数", verbose_name="有效期(天)")

    class Meta:
        verbose_name = "会员卡产品"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', '待支付'), 
        ('paid', '已支付'),
        ('refunding', '退款中'),
        ('refunded', '已退款'),
        ('failed', '支付失败/已关闭')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    product = models.ForeignKey(MembershipProduct, on_delete=models.CASCADE, verbose_name="购买产品")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="支付金额")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', verbose_name="订单状态")
    out_trade_no = models.CharField(max_length=64, unique=True, null=True, blank=True, verbose_name="商户订单号")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "支付订单"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

class Refund(models.Model):
    STATUS_CHOICES = (
        ('pending', '退款处理中'),
        ('success', '退款成功'),
        ('failed', '退款失败')
    )
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='refund', verbose_name="关联订单")
    reason = models.CharField(max_length=255, blank=True, verbose_name="退款原因")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', verbose_name="退款状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="申请时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "退款申请"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"退款 - {self.order.id}"
