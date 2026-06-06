from django.urls import path
from .views import ProductListView, PurchaseView, OrderStatusView, RefundApplyView, RefundStatusView, RedeemView, WechatPayNotifyView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product_list'),
    path('purchase/', PurchaseView.as_view(), name='purchase'),
    path('status/', OrderStatusView.as_view(), name='order_status'),
    path('refund/apply/', RefundApplyView.as_view(), name='refund_apply'),
    path('refund/status/', RefundStatusView.as_view(), name='refund_status'),
    path('redeem/', RedeemView.as_view(), name='redeem'),
    path('wechat/notify/', WechatPayNotifyView.as_view(), name='wechat_notify'),
]
