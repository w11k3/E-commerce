from django.urls import path
from .views import (
    adicionar_carrinho,
    comprar_agora,
    ver_carrinho,
    alterar_quantidade,
    remover_carrinho,
    checkout,
    finalizar_compra,
    compra_finalizada,
)

urlpatterns = [
    path('', ver_carrinho, name='carrinho'),
    path('adicionar/<int:produto_id>/', adicionar_carrinho,
         name='adicionar_carrinho'),
    path('comprar-agora/<int:produto_id>/', comprar_agora,
         name='comprar_agora'),
    path('quantidade/<int:item_id>/<str:acao>/', alterar_quantidade,
         name='alterar_quantidade'),
    path('remover/<int:item_id>/', remover_carrinho,
         name='remover_carrinho'),
    path('checkout/', checkout, name='checkout'),
    path("finalizar/", finalizar_compra, name="finalizar_compra"),
    path("finalizado/", compra_finalizada, name="compra_finalizada"),
]