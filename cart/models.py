from django.db import models
from django.conf import settings
from products.models import Produto, Tamanho


class ItemCarrinho(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE
    )
    # Tamanho escolhido (vazio para produtos sem tamanhos cadastrados).
    tamanho = models.ForeignKey(
        Tamanho,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    quantidade = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.produto.nome} - {self.quantidade}'