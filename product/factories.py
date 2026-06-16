import factory

from product.models import Product
from product.models import Category

class CategoryFactory(factory.django.DjangoModelFactory):
  title = factory.Faker('word')
  slug = factory.Faker('slug')
  description = factory.Faker('text')
  active = True

  class Meta:
    model = Category

class ProductFactory(factory.django.DjangoModelFactory):
  price = factory.Faker('pyint')
  title = factory.Faker('word')

  @factory.post_generation
  def category(self, create, extracted, **kwargs):
    if not create:
      return
    if extracted is not None:
      for category in extracted:
        self.category.add(category)
    else:
      self.category.add(CategoryFactory())

  class Meta:
    model = Product