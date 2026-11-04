from django.urls import path
from .views import (
    HomeView,
    DepartamentoView,
    BuscaView,
    ProdutoDetailView,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    # <str:publico> e <int:pk> são partes dinâmicas da url:
    # o valor chega na view em self.kwargs
    path('departamento/<str:publico>/', DepartamentoView.as_view(),
         name='departamento'),
    path('departamento/<str:publico>/<slug:categoria_slug>/',
         DepartamentoView.as_view(), name='departamento_categoria'),

    path('buscar/', BuscaView.as_view(), name='busca'),
    path('produto/<int:pk>/', ProdutoDetailView.as_view(),
         name='produto_detalhe'),
]