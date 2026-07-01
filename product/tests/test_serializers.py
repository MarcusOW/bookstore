import pytest
from decimal import Decimal
from product.serializers import CategorySerializer, ProductSerializer
from product.factories import CategoryFactory, ProductFactory

# ===================== CategorySerializer Tests =====================


@pytest.mark.django_db
class TestCategorySerializer:

    def test_serialize_category(self):
        category = CategoryFactory(title="Eletrônicos", slug="eletronicos")
        serializer = CategorySerializer(category)
        data = serializer.data
        assert data["title"] == "Eletrônicos"
        assert data["slug"] == "eletronicos"
        assert "description" in data
        assert "active" in data
        assert "id" not in data

    def test_deserialize_valid_data(self):
        data = {
            "title": "Livros",
            "slug": "livros",
            "description": "Categoria para livros",
            "active": True,
        }
        serializer = CategorySerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        category = serializer.save()
        assert category.title == "Livros"
        assert category.slug == "livros"
        assert category.description == "Categoria para livros"
        assert category.active is True

    def test_slug_unique_validation(self):
        CategoryFactory(slug="unico")
        data = {"title": "Outro", "slug": "unico"}
        serializer = CategorySerializer(data=data)
        assert not serializer.is_valid()
        assert "slug" in serializer.errors

    def test_title_required(self):
        data = {"slug": "sem-titulo"}
        serializer = CategorySerializer(data=data)
        assert not serializer.is_valid()
        assert "title" in serializer.errors

    def test_active_default_true(self):
        data = {"title": "Padrão", "slug": "padrao"}
        serializer = CategorySerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        category = serializer.save()
        assert category.active is True

    def test_description_optional(self):
        data = {"title": "Sem desc", "slug": "sem-desc", "description": None}
        serializer = CategorySerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        category = serializer.save()
        assert category.description is None

    def test_active_false(self):
        data = {"title": "Inativo", "slug": "inativo", "active": False}
        serializer = CategorySerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        category = serializer.save()
        assert category.active is False


# ===================== ProductSerializer Tests =====================


@pytest.mark.django_db
class TestProductSerializer:

    def test_serialize_product(self):
        product = ProductFactory(title="Notebook", price=Decimal("2500.00"))
        serializer = ProductSerializer(product)
        data = serializer.data
        assert data["title"] == "Notebook"
        assert data["price"] == 2500
        assert "description" in data
        assert "active" in data
        assert "category" in data
        assert isinstance(data["category"], list)
        assert len(data["category"]) == 1

    def test_serialize_product_with_multiple_categories(self):
        cat1 = CategoryFactory()
        cat2 = CategoryFactory()
        product = ProductFactory(category=[cat1, cat2])
        serializer = ProductSerializer(product)
        categories_data = serializer.data["category"]
        assert len(categories_data) == 2
        titles = [cat["title"] for cat in categories_data]
        assert cat1.title in titles
        assert cat2.title in titles

    def test_deserialize_valid_data(self):
        category = CategoryFactory()
        data = {
            "title": "Mouse",
            "price": 50,
            "description": "Mouse óptico",
            "active": True,
            "categories_id": [category.id],
        }
        serializer = ProductSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        product = serializer.save()
        assert product.title == "Mouse"
        assert product.price == 50
        assert category in product.category.all()
        assert product.category.count() == 1

    def test_create_product_without_category(self):
        data = {"title": "Teclado", "price": "120.00", "categories_id": []}
        serializer = ProductSerializer(data=data)
        assert not serializer.is_valid()
        assert "categories_id" in serializer.errors
        assert serializer.errors["categories_id"][0] == "This list may not be empty."

    def test_price_must_be_positive(self):
        data = {"title": "Produto", "price": "-10.00", "category": []}
        serializer = ProductSerializer(data=data)
        assert not serializer.is_valid()
        assert "price" in serializer.errors

    def test_title_required(self):
        data = {"price": "99.99", "category": []}
        serializer = ProductSerializer(data=data)
        assert not serializer.is_valid()
        assert "title" in serializer.errors

    def test_category_required(self):
        data = {"title": "Produto", "price": "10.00"}
        serializer = ProductSerializer(data=data)
        assert not serializer.is_valid()
        assert "categories_id" in serializer.errors

    def test_active_default_true(self):
        category = CategoryFactory()
        data = {
            "title": "Produto",
            "price": "10.00",
            "categories_id": [category.id],
        }
        serializer = ProductSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        product = serializer.save()
        assert product.active is True

    def test_update_product(self):
        product = ProductFactory(title="Antigo")
        data = {"title": "Novo Título"}
        serializer = ProductSerializer(instance=product, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        assert updated.title == "Novo Título"
