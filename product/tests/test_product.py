import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from product.models import Product, Category
from product.factories import ProductFactory, CategoryFactory

@pytest.mark.django_db
class TestProduct:

    def test_create_product_with_minimal_fields(self):
        product = ProductFactory(title='Notebook', price=2500, active=True)
        assert product.title == 'Notebook'
        assert product.price == 2500
        assert product.active is True
        assert product.description is None
        product2 = Product.objects.create(title='Mouse', price=50)
        assert product2.description is None
        assert product2.active is True  # default

    def test_product_description_optional(self):
        product = ProductFactory(description=None)
        assert product.description is None
        
        product2 = ProductFactory(description='')
        assert product2.description == ''

    def test_price_can_be_null(self):
        product = ProductFactory(price=None)
        assert product.price is None

    def test_price_positive_integer(self):
        product = ProductFactory(price=100)
        assert product.price == 100
        with pytest.raises(ValidationError):
            p = Product(price=-10)
            p.full_clean()

    def test_active_default_true(self):
        product = Product.objects.create(title='Tablet', price=300)
        assert product.active is True

    def test_category_many_to_many_relationship(self):
        product = ProductFactory()
        assert product.category.count() == 1
        assert isinstance(product.category.first(), Category)

    def test_product_add_multiple_categories(self):
        cat1 = CategoryFactory(slug='cat1')
        cat2 = CategoryFactory(slug='cat2')
        product = ProductFactory(category=[cat1, cat2])
        assert product.category.count() == 2
        assert cat1 in product.category.all()
        assert cat2 in product.category.all()

    def test_product_without_any_category(self):
        product = ProductFactory(category=[])
        assert product.category.count() == 0

    def test_string_representation(self):
        product = ProductFactory(title='Smartphone')
        assert str(product) == product.title

    def test_title_max_length(self):
        long_title = 'a' * 101
        product = Product(title=long_title, price=10)
        with pytest.raises(ValidationError):
            product.full_clean()