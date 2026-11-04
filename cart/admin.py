from django.contrib import admin
from .models import ItemCarrinho


@admin.register(ItemCarrinho)
class ItemCarrinhoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'produto', 'tamanho', 'quantidade')
    list_filter = ('produto__categoria',)
    search_fields = (
        'usuario__email',
        'produto__nome',
    )
    list_select_related = ('usuario', 'produto')
    ordering = ('usuario__email', 'produto__nome')
    list_per_page = 20