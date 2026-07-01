from rest_framework import serializers
from order.models import Order
from product.models import Product
from product.serializers.product_serializer import ProductSerializer


class OrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True, many=True)
    products_ids = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        many=True,
        allow_empty=False,
    )
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "products_ids", "user", "product", "total"]

    def get_total(self, instance):
        total = sum([product.price for product in instance.product.all()])
        return total

    def create(self, validated_data):
        product_data = validated_data.pop("products_ids")
        user_data = validated_data.pop("user")

        order = Order.objects.create(user=user_data)
        order.product.add(*product_data)

        return order
