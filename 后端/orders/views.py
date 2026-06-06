from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, inline_serializer
from django.db import transaction
from .models import MembershipProduct, Order, Refund
from .serializers import MembershipProductSerializer, OrderSerializer
from datetime import date, timedelta
from common.api import ok, fail
from common.demo_content import (
    build_order_content,
    ensure_demo_membership_products,
    get_product_template,
)
import uuid
import os
import time
import random
import string
from django.conf import settings
from wechatpy.pay import WeChatPay

# 初始化微信支付客户端
def get_wechat_pay():
    appid = os.environ.get("WECHAT_APPID", "wx_mock_appid")
    api_key = os.environ.get("WECHAT_PAY_API_KEY", "mock_api_key_for_wechat_pay_1234567")
    mch_id = os.environ.get("WECHAT_MCH_ID", "1234567890")
    mch_cert = os.environ.get("WECHAT_MCH_CERT", "") # 证书路径
    mch_key = os.environ.get("WECHAT_MCH_KEY", "")   # 证书私钥路径
    
    return WeChatPay(
        appid=appid,
        api_key=api_key,
        mch_id=mch_id,
        mch_cert=mch_cert,
        mch_key=mch_key
    )

ProductListEnvelopeSerializer = inline_serializer(
    name="ProductListEnvelope",
    fields={
        "code": serializers.IntegerField(),
        "message": serializers.CharField(),
        "data": inline_serializer(
            name="ProductListData",
            fields={
                "products": MembershipProductSerializer(many=True),
                "recommendation": serializers.CharField(),
            },
        ),
    },
)

class ProductListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiResponse(response=ProductListEnvelopeSerializer)})
    def get(self, request):
        ensure_demo_membership_products()
        qs = MembershipProduct.objects.all().order_by("days_duration")
        serializer = MembershipProductSerializer(qs, many=True)
        enriched_list = []
        for item in serializer.data:
            product_copy = get_product_template(item.get("name"))
            enriched_list.append(
                {
                    **item,
                    "description": product_copy.get("description", ""),
                    "duration_text": f"{item.get('days_duration', 0)}天" if item.get("days_duration") else "",
                }
            )
        return ok(
            {
                "products": enriched_list,
                "recommendation": build_order_content()["payment_simulation_note"],
            },
            message="获取成功",
        )

class OrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="order_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
            )
        ],
        responses=inline_serializer(
            name="OrderStatusEnvelope",
            fields={
                "code": serializers.IntegerField(),
                "message": serializers.CharField(),
                "data": inline_serializer(
                    name="OrderStatusData",
                    fields={
                        "order_id": serializers.IntegerField(),
                        "status": serializers.CharField(),
                        "product_name": serializers.CharField(),
                        "amount": serializers.CharField(),
                        "created_at": serializers.DateTimeField(),
                        "order_status_note": serializers.CharField(),
                        "refund_note": serializers.CharField(),
                    },
                ),
            },
        ),
    )
    def get(self, request):
        ensure_demo_membership_products()
        order_id = request.query_params.get('order_id')
        if not order_id:
            return fail("缺少 order_id", code=400, http_status=400)
        
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            return ok({
                "order_id": order.id,
                "status": order.status,
                "product_name": order.product.name,
                "amount": order.amount,
                "created_at": order.created_at,
                "order_status_note": build_order_content()["order_status_note"],
                "refund_note": build_order_content()["refund_note"],
            }, message="获取成功")
        except Order.DoesNotExist:
            return fail("订单不存在", code=404, http_status=404)

class PurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=inline_serializer(
            name="PurchaseRequest",
            fields={"product_id": serializers.IntegerField()},
        ),
        responses=inline_serializer(
            name="PurchaseEnvelope",
            fields={
                "code": serializers.IntegerField(),
                "message": serializers.CharField(),
                "data": inline_serializer(
                    name="PurchaseData",
                    fields={
                        "order_id": serializers.IntegerField(),
                        "timeStamp": serializers.CharField(),
                        "nonceStr": serializers.CharField(),
                        "package": serializers.CharField(),
                        "signType": serializers.CharField(),
                        "paySign": serializers.CharField(),
                    },
                ),
            },
        ),
    )
    def post(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        ensure_demo_membership_products()

        if not product_id:
            return fail("缺少 product_id", code=400, http_status=400)

        try:
            product = MembershipProduct.objects.get(id=product_id)
        except MembershipProduct.DoesNotExist:
            return fail("产品不存在", code=404, http_status=404)

        # 获取微信 OpenID 
        openid = getattr(user, 'openid', None)
        if not openid:
            # 临时 Mock 保证流程能跑通
            openid = "mock_user_openid_12345"

        with transaction.atomic():
            user_obj = type(request.user).objects.select_for_update().get(id=request.user.id)
            if user_obj.balance < product.price:
                return fail("余额不足，请充值", code=400, http_status=400)

            # 1. 创建订单
            order = Order.objects.create(
                user=user,
                product=product,
                amount=product.price,
                status='paid'  # 余额支付直接成功
            )

            # 生成商户订单号
            out_trade_no = f"TR{order.id:08d}{int(time.time())}"
            order.out_trade_no = out_trade_no
            order.save(update_fields=['out_trade_no'])

            # 2. 扣除余额
            user_obj.balance -= product.price

            # 3. 下发会员权益
            if not user_obj.membership_expiry or user_obj.membership_expiry < date.today():
                user_obj.membership_expiry = date.today() + timedelta(days=product.days_duration)
            else:
                user_obj.membership_expiry += timedelta(days=product.days_duration)
            
            user_obj.save(update_fields=['balance', 'membership_expiry'])

            return ok({
                "order_id": order.id,
                "new_balance": user_obj.balance,
                "new_expiry": user_obj.membership_expiry.strftime('%Y-%m-%d'),
                "order_status_note": build_order_content()["order_status_note"],
                "refund_note": build_order_content()["refund_note"],
            }, message="支付成功，会员权益已生效", http_status=status.HTTP_201_CREATED)

class WechatPayNotifyView(APIView):
    # 回调接口不需要 JWT 认证
    permission_classes = []
    
    def post(self, request):
        try:
            wxpay = get_wechat_pay()
            # 真实环境中获取原始 XML 数据
            # raw_data = request.body
            # parsed_data = wxpay.parse_payment_result(raw_data)
            
            # 模拟解析出的数据
            parsed_data = {
                "out_trade_no": "TR000000121711612000",
                "result_code": "SUCCESS",
                "total_fee": 1000
            }

            if parsed_data.get('result_code') == 'SUCCESS':
                out_trade_no = parsed_data.get('out_trade_no')
                
                with transaction.atomic():
                    # 锁定订单防止并发回调
                    try:
                        order = Order.objects.select_for_update().get(out_trade_no=out_trade_no)
                    except Order.DoesNotExist:
                        return Response("<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>", content_type="application/xml")

                    if order.status == 'pending':
                        # 更新订单状态
                        order.status = 'paid'
                        order.save(update_fields=['status'])
                        
                        # 锁定用户并更新权益
                        user_obj = type(order.user).objects.select_for_update().get(id=order.user.id)
                        today = date.today()
                        
                        if user_obj.membership_expiry and user_obj.membership_expiry >= today:
                            user_obj.membership_expiry += timedelta(days=order.product.days_duration)
                        else:
                            user_obj.membership_expiry = today + timedelta(days=order.product.days_duration)
                        
                        user_obj.save(update_fields=['membership_expiry'])

            # 无论业务处理是否成功，只要验签通过都返回成功给微信，防止微信不断重发
            return Response(
                "<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>",
                content_type="application/xml"
            )

        except Exception as e:
            # 验签失败或其它异常，返回 FAIL
            return Response(
                f"<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[{str(e)}]]></return_msg></xml>",
                content_type="application/xml"
            )

class RefundApplyView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=inline_serializer(
            name="RefundApplyRequest",
            fields={
                "order_id": serializers.IntegerField(),
                "reason": serializers.CharField(required=False, allow_blank=True),
            },
        ),
        responses=inline_serializer(
            name="RefundApplyEnvelope",
            fields={
                "code": serializers.IntegerField(),
                "message": serializers.CharField(),
                "data": inline_serializer(
                    name="RefundApplyData",
                    fields={
                        "refund_id": serializers.IntegerField(),
                        "status": serializers.CharField(),
                        "new_balance": serializers.CharField(),
                    },
                ),
            },
        ),
    )
    def post(self, request):
        order_id = request.data.get('order_id')
        reason = request.data.get('reason', '用户主动发起退款')

        if not order_id:
            return fail("缺少 order_id", code=400, http_status=400)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return fail("订单不存在", code=404, http_status=404)

        if order.status != 'paid':
            return fail("该订单无法申请退款", code=400, http_status=400)

        with transaction.atomic():
            # 锁定订单
            order = Order.objects.select_for_update().get(id=order.id)
            if hasattr(order, 'refund') or order.status != 'paid':
                return fail("退款申请正在处理或已处理", code=400, http_status=400)

            # 更新订单状态并创建退款记录
            order.status = 'refunding'
            order.save(update_fields=['status'])

            refund = Refund.objects.create(
                order=order,
                reason=reason,
                status='pending'
            )

            # 在真实业务中，这里会调用第三方支付退款接口，目前模拟自动退款成功
            # 模拟退款成功：将状态设为成功，并退还余额，扣减权益
            refund.status = 'success'
            refund.save(update_fields=['status'])
            
            order.status = 'refunded'
            order.save(update_fields=['status'])

            user_obj = type(request.user).objects.select_for_update().get(id=request.user.id)
            user_obj.balance += order.amount
            
            # 简单扣减会员天数 (实际业务中需要更严谨的权益计算)
            if user_obj.membership_expiry:
                user_obj.membership_expiry -= timedelta(days=order.product.days_duration)
                if user_obj.membership_expiry < date.today():
                    user_obj.membership_expiry = None
            user_obj.save()

            return ok({
                "refund_id": refund.id,
                "status": "refunded",
                "new_balance": user_obj.balance
            }, message="退款申请成功并已完成退款")


class RefundStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="order_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
            )
        ],
        responses=inline_serializer(
            name="RefundStatusEnvelope",
            fields={
                "code": serializers.IntegerField(),
                "message": serializers.CharField(),
                "data": inline_serializer(
                    name="RefundStatusData",
                    fields={
                        "refund_id": serializers.IntegerField(),
                        "order_id": serializers.IntegerField(),
                        "refund_status": serializers.CharField(),
                        "reason": serializers.CharField(),
                        "created_at": serializers.DateTimeField(),
                        "refund_note": serializers.CharField(),
                    },
                ),
            },
        ),
    )
    def get(self, request):
        order_id = request.query_params.get('order_id')
        if not order_id:
            return fail("缺少 order_id", code=400, http_status=400)
        
        try:
            refund = Refund.objects.get(order__id=order_id, order__user=request.user)
            return ok({
                "refund_id": refund.id,
                "order_id": refund.order.id,
                "refund_status": refund.status,
                "reason": refund.reason,
                "created_at": refund.created_at,
                "refund_note": build_order_content()["refund_note"],
            }, message="获取成功")
        except Refund.DoesNotExist:
            # 订单详情页会默认拉取退款状态；未发起退款时返回空状态即可，避免前端出现 404 噪音。
            return ok({
                "refund_id": None,
                "order_id": int(order_id),
                "refund_status": "",
                "reason": "",
                "created_at": None,
                "refund_note": "",
            }, message="当前订单暂无退款记录")

class RedeemView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=inline_serializer(
            name="RedeemRequest",
            fields={
                "platform": serializers.CharField(required=False, default="meituan"),
                "coupon_code": serializers.CharField(required=True),
            },
        ),
        responses=inline_serializer(
            name="RedeemEnvelope",
            fields={
                "code": serializers.IntegerField(),
                "message": serializers.CharField(),
                "data": inline_serializer(
                    name="RedeemData",
                    fields={
                        "product_name": serializers.CharField(),
                        "valid_until": serializers.CharField(),
                    },
                ),
            },
        ),
    )
    def post(self, request):
        coupon_code = request.data.get('coupon_code')
        if not coupon_code:
            return fail("请输入券码", code=400, http_status=400)
        
        # 简单模拟核销逻辑，给用户增加1天体验卡
        user_obj = request.user
        today = date.today()
        
        with transaction.atomic():
            user_obj = type(user_obj).objects.select_for_update().get(id=user_obj.id)
            
            if user_obj.membership_expiry and user_obj.membership_expiry >= today:
                user_obj.membership_expiry += timedelta(days=1)
            else:
                user_obj.membership_expiry = today + timedelta(days=1)
            
            user_obj.save()

        return ok({
            "product_name": "单次体验卡",
            "valid_until": user_obj.membership_expiry.strftime("%Y-%m-%d")
        }, message="核销成功")
