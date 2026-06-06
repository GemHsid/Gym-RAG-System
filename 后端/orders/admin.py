from django.contrib import admin
from .models import MembershipProduct, Order, Refund
from common.admin_mixins import ExportExcelMixin

@admin.register(MembershipProduct)
class MembershipProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'days_duration')
    search_fields = ('name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ('id', 'user', 'product', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id', 'product__name')
    actions = ['export_as_excel']

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ('id', 'order', 'status', 'reason', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__user__username', 'reason')
    actions = ['export_as_excel']
