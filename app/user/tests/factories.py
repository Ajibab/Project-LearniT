import factory
from django.contrib.auth.models import User
from faker import Faker 
from .models import User, Token

"""Factory is created for the User and Token Models to generate testing data"""

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    email = factory.Sequence(lambda n: 'name{}@example.com'.format(n))
    first_name = fake.name()
    surname = fake.name()
    password = factory.PostGenerationMethod('set_password','passes@@@1233')
    verified ='True'
    @classmethod
    def _prepare(cls,create,**kwargs):
        password = kwargs.pop("password", None)
        user = super(UserFactory,cls)._prepare(create,**kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user

class TokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Token
    token = fake.md5()

class TokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model =Token
    token = 1234

