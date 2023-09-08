from django.db import models
from django.contrib.auth.models import AbstractUser
from ..proyecto import settings
import jwt
# Create your models here.


class User(AbstractUser):
    is_admin=models.BooleanField('is_admin', default=False)
    is_customer=models.BooleanField('is_customer', default=False)
    is_employee=models.BooleanField('is_employee', default=False)

def get_token(self):
       

        payload = {
            'username': self.username,
            'password': self.password,
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        return token