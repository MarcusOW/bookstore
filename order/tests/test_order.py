import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from product.models.product import Product
from order.models import Order
from order.factories import OrderFactory, UserFactory
from product.factories import ProductFactory

@pytest.mark.django_db
class TestOrder:

    def test_create_order_with_user_and_one_product(self):
        user = UserFactory()
        product = ProductFactory()
        order = OrderFactory(user=user, product=[product])
        assert order.user == user
        assert order.product.count() == 1
        assert product in order.product.all()

    def test_create_order_with_multiple_products(self):
        user = UserFactory()
        products = ProductFactory.create_batch(3)
        order = OrderFactory(user=user, product=products)
        assert order.product.count() == 3
        for p in products:
            assert p in order.product.all()

    def test_order_requires_user(self):
        with pytest.raises(IntegrityError):
            Order.objects.create(user=None)

    def test_order_user_on_delete_cascade(self):
        user = UserFactory()
        order = OrderFactory(user=user)
        user.delete()
        with pytest.raises(Order.DoesNotExist):
            Order.objects.get(id=order.id)

    def test_order_str_method(self):
        order = OrderFactory()
        assert str(order) == f"Order {order.id} - {order.user.username}"

    def test_add_product_to_existing_order(self):
        order = OrderFactory()
        new_product = ProductFactory()
        order.product.add(new_product)
        assert order.product.count() == 2
        assert new_product in order.product.all()

    def test_remove_product_from_order(self):
        products = ProductFactory.create_batch(2)
        order = OrderFactory(product=products)
        order.product.remove(products[0])
        assert order.product.count() == 1
        assert products[0] not in order.product.all()

    def test_order_products_are_distinct(self):
        product = ProductFactory()
        order = OrderFactory(product=[product])
        order.product.add(product)
        assert order.product.count() == 1