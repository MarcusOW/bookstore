# product/serializers.py
from rest_framework import serializers
from product.models import Product, Category

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all(), allow_empty=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'active', 'category']