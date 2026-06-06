from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import MembershipProduct, Order

class MembershipProductSerializer(serializers.ModelSerializer):
    original_price = serializers.SerializerMethodField()
    tags = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = MembershipProduct
        fields = ['id', 'name', 'price', 'original_price', 'days_duration', 'tags', 'is_promotion']

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_original_price(self, obj):
        value = obj.original_price if obj.original_price is not None else obj.price
        if value is None:
            return None
        return f"{value:.2f}"

class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'product', 'product_name', 'amount', 'status', 'created_at']
        read_only_fields = ['amount', 'status', 'created_at']
