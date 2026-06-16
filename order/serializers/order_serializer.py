from rest_framework import serializers
from order.models import Order
from product.models import Product

class OrderSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all(), allow_empty=False)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'product', 'total']
        read_only_fields = ['id', 'total']

    def get_total(self, obj):
        return sum(p.price for p in obj.product.all())