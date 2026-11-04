from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nome', 'sobrenome']

    def __str__(self):
        return self.email