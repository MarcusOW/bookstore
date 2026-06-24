import json
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse

from product.factories import CategoryFactory, ProductFactory
from product.models import Product
from order.factories import UserFactory

class TestProductViewSet(APITestCase):
  client = APIClient()

  def setUp(self):
    self.user = UserFactory()
    self.client.force_authenticate(user=self.user)
    self.product = ProductFactory(title='pro controller', price=200)

  def test_get_all_products(self):
    response = self.client.get(
      reverse('product-list', kwargs={'version': 'v1'})
    )
    self.assertEqual(response.status_code, status.HTTP_200_OK)

    data = response.json()
    if isinstance(data, list):
      products = data
    else:
      products = data.get('results', [])

    self.assertGreater(len(products), 0, "Nenhum produto retornado")
    product_data = products[0]
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