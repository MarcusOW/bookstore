from rest_framework import serializers
from product.models import Product, Category
from product.serializers.category_serializer import CategorySerializer

class ProductSerializer(serializers.ModelSerializer):
  category = CategorySerializer(read_only=True, many=True)
  categories_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True, allow_empty=False, many=True)

  class Meta:
    model = Product
    fields = ['id', 'title', 'description', 'price', 'active', 'category', 'categories_id']

  def create(self, validated_data):
    category_data = validated_data.pop('categories_id')

    product = Product.objects.create(**validated_data)
    product.category.add(*category_data)

    return product