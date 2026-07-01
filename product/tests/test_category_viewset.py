import json
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse

from product.factories import CategoryFactory
from product.models import Category
from order.factories import UserFactory


class TestCategoryViewSet(APITestCase):
    client = APIClient()

    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.category = CategoryFactory(title="books")

    def test_get_all_categories(self):
        response = self.client.get(reverse("category-list", kwargs={"version": "v1"}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        if isinstance(data, list):
            categories = data
        else:
            categories = data.get("results", [])

        self.assertGreater(len(categories), 0, "Nenhuma categoria retornada")
        category_data = categories[0]
        self.assertEqual(category_data["title"], self.category.title)

    def test_create_category(self):
        data = json.dumps({"title": "technology"})
        response = self.client.post(
            reverse("category-list", kwargs={"version": "v1"}),
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_category = Category.objects.get(title="technology")
        self.assertEqual(created_category.title, "technology")
        self.assertIsNotNone(created_category.slug)
