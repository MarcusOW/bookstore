import factory

from django.contrib.auth.models import User
from product.factories import ProductFactory

from order.models import Order

class UserFactory(factory.django.DjangoModelFactory):
  email = factory.Faker('email')
  username = factory.Faker('user_name')

  class Meta:
    model = User
    skip_postgeneration_save = True

class OrderFactory(factory.django.DjangoModelFactory):
  user = factory.SubFactory(UserFactory)

  @factory.post_generation
  def product(self, create, extracted, **kwargs):
    if not create:
      return
    if extracted is not None:
      for product in extracted:
        self.product.add(product)
    else:
        self.product.add(ProductFactory())

  class Meta:
    model = Order
    skip_postgeneration_save = True