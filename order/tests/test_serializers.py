import pytest
from django.contrib.auth.models import User
from order.serializers import OrderSerializer
from order.factories import OrderFactory, UserFactory
from product.factories import ProductFactory

@pytest.mark.django_db
class TestOrderSerializer:

    def test_serialize_order(self):
        order = OrderFactory()  # já cria com 1 produto
        serializer = OrderSerializer(order)
        data = serializer.data
        assert 'id' in data
        assert 'user' in data
        assert 'product' in data
        assert 'total' in data
        assert isinstance(data['product'], list)
        assert data['total'] == order.product.first().price  # só 1 produto

    def test_deserialize_valid_data(self):
        user = UserFactory()
        product = ProductFactory()
        data = {
            'user': user.id,
            'product': [product.id]
        }
        serializer = OrderSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        order = serializer.save()
        assert order.user == user

    def test_total_calculation_with_multiple_products(self):
        products = ProductFactory.create_batch(3, price=100)
        order = OrderFactory(product=products)
        serializer = OrderSerializer(order)
        assert serializer.data['total'] == 300

    def test_product_required(self):
        user = UserFactory()
        data = {'user': user.id, 'product': []}
        serializer = OrderSerializer(data=data)
        # blank=False no modelo, mas serializer com required=True deve rejeitar lista vazia
        assert not serializer.is_valid()
        assert 'product' in serializer.errors

    def test_product_must_exist(self):
        user = UserFactory()
        data = {'user': user.id, 'product': [9999]}
        serializer = OrderSerializer(data=data)
        assert not serializer.is_valid()
        assert 'product' in serializer.errors