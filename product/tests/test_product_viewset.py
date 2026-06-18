import json
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse

from product.factories import CategoryFactory, ProductFactory
from order.factories import UserFactory
from product.models import Product

class TestProductViewSet(APITestCase):
  client = APIClient()

  def setUp(self):
    self.product = ProductFactory(title='pro controller', price=200)
    self.user = UserFactory()

  def test_get_all_products(self):
    response = self.client.get(
      reverse('product-list', kwargs={'version': 'v1'})
    )
    self.assertEqual(response.status_code, status.HTTP_200_OK)

    products_data = response.json()
    self.assertGreaterEqual(len(products_data), 1)

    product_data = products_data[0]
    self.assertEqual(product_data['title'], self.product.title)
    self.assertEqual(product_data['price'], self.product.price)
    self.assertEqual(product_data['active'], self.product.active)

  def test_create_product(self):
    category = CategoryFactory()
    data = json.dumps({
      'title': 'notebook',
      'price': 800,
      'categories_id': [category.id]
    })

    response = self.client.post(
      reverse('product-list', kwargs={'version': 'v1'}),
      data=data,
      content_type='application/json'
    )

    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    created_product = Product.objects.get(title='notebook')
    self.assertEqual(created_product.title, 'notebook')
    self.assertEqual(created_product.price, 800)
    self.assertEqual(created_product.category.count(), 1)
    self.assertEqual(created_product.category.first().id, category.id)