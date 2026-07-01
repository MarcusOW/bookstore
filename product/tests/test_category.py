import pytest
from django.db import IntegrityError
from product.factories import CategoryFactory


@pytest.mark.django_db
class TestCategory:

    def test_create_category_with_all_fields(self):
        category = CategoryFactory(
            title="Tech",
            slug="tech-news",
            description="All about technology",
            active=True,
        )
        assert category.title == "Tech"
        assert category.slug == "tech-news"
        assert category.description == "All about technology"
        assert category.active is True

    def test_category_slug_must_be_unique(self):
        CategoryFactory(slug="unique-slug")
        with pytest.raises(IntegrityError):
            CategoryFactory(slug="unique-slug")

    def test_description_can_be_null_and_blank(self):
        category = CategoryFactory(description=None)
        assert category.description is None

        category2 = CategoryFactory(description="")
        assert category2.description == ""

    def test_active_defaults_to_true(self):
        category = CategoryFactory()
        assert category.active is True

    def test_unicode_method_returns_title(self):
        category = CategoryFactory(title="Python")
        assert str(category) == "Python"
