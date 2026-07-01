import json
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.urls import reverse

from product.factories import CategoryFactory, ProductFactory
from order.factories import OrderFactory, UserFactory
from order.models import Order


class TestOrderViewSet(APITestCase):
    client = APIClient()

    def setUp(self):
        self.category = CategoryFactory(title="technology")
        self.product = ProductFactory(title="mouse", price=100, category=[self.category])
        self.order = OrderFactory(product=[self.product])
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_order_list(self):
        response = self.client.get(reverse("order-list", kwargs={"version": "v1"}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        if isinstance(data, list):
            orders = data
        else:
            orders = data.get("results", [])

        self.assertGreater(len(orders), 0, "Nenhum pedido retornado")
        order_data = orders[0]

        product_data = order_data["product"][0]
        self.assertEqual(product_data["title"], self.product.title)
        self.assertEqual(product_data["price"], self.product.price)
        self.assertEqual(product_data["active"], self.product.active)

        category_data = product_data["category"][0]
        self.assertEqual(category_data["title"], self.category.title)

        self.assertEqual(order_data["total"], self.product.price)

    def test_create_order(self):
        product = ProductFactory(price=50)
        payload = {"products_ids": [product.id], "user": self.user.id}
        response = self.client.post(
            reverse("order-list", kwargs={"version": "v1"}),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_order = Order.objects.get(user=self.user)
        self.assertEqual(created_order.product.count(), 1)
        self.assertEqual(created_order.product.first().id, product.id)
        self.assertEqual(response.data["total"], product.price)
