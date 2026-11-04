from django.contrib import admin
from .models import Banner, Categoria, Produto, Tamanho


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug', 'total_produtos')
    search_fields = ('nome',)
    prepopulated_fields = {'slug': ('nome',)}
    ordering = ('nome',)

    @admin.display(description='Produtos')
    def total_produtos(self, obj):
        return obj.produtos.count()


@admin.register(Tamanho)
class TamanhoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'categoria',
        'genero',
        'preco',
        'preco_promocional',
        'estoque',
        'em_promocao',
    )

    list_filter = ('genero', 'categoria')
    search_fields = ('nome', 'descricao', 'categoria__nome')
    list_select_related = ('categoria',)
    filter_horizontal = ('tamanhos',)
    ordering = ('nome',)
    list_per_page = 25
    readonly_fields = ('criado_em',)

    fieldsets = (
        ('Informações do produto', {
            'fields': (
                'nome',
                'categoria',
                'genero',
                'descricao',
                'imagem',
            )
        }),
        ('Preço e estoque', {
            'fields': (
                'preco',
                'preco_promocional',
                'estoque',
            )
        }),
        ('Tamanhos disponíveis', {
            'fields': ('tamanhos',)
        }),
        ('Registro', {
            'fields': ('criado_em',)
        }),
    )


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'ordem', 'ativo', 'tem_imagem')
    list_editable = ('ordem', 'ativo')

    @admin.display(boolean=True, description='Imagem')
    def tem_imagem(self, obj):
        return bool(obj.imagem)














# from django.contrib import admin
# from .models import Banner, Categoria, Produto, Tamanho


# @admin.register(Categoria)
# class CategoriaAdmin(admin.ModelAdmin):
#     list_display = ('nome', 'slug', 'total_produtos')
#     search_fields = ('nome',)
#     prepopulated_fields = {'slug': ('nome',)}
#     ordering = ('nome',)

#     @admin.display(description='Produtos')
#     def total_produtos(self, obj):
#         return obj.produtos.count()


# @admin.register(Tamanho)
# class TamanhoAdmin(admin.ModelAdmin):
#     list_display = ('nome',)
#     search_fields = ('nome',)


# @admin.register(Produto)
# class ProdutoAdmin(admin.ModelAdmin):
#     list_display = (
#         'nome',
#         'categoria',
#         'publico',
#         'preco',
#         'preco_promocional',
#         'estoque',
#         'em_promocao',
#     )
#     list_filter = ('publico', 'categoria')
#     search_fields = ('nome', 'descricao', 'categoria__nome')
#     list_select_related = ('categoria',)
#     filter_horizontal = ('tamanhos',)
#     ordering = ('nome',)
#     list_per_page = 25
#     readonly_fields = ('criado_em',)

#     fieldsets = (
#         ('Informações do produto', {
#             'fields': (
#                 'nome',
#                 'categoria',
#                 'publico',
#                 'descricao',
#                 'imagem',
#             )
#         }),
#         ('Preço e estoque', {
#             'fields': (
#                 'preco',
#                 'preco_promocional',
#                 'estoque',
#             )
#         }),
#         ('Tamanhos disponíveis', {
#             'fields': ('tamanhos',)
#         }),
#         ('Registro', {
#             'fields': ('criado_em',)
#         }),
#     )


# @admin.register(Banner)
# class BannerAdmin(admin.ModelAdmin):
#     list_display = ('__str__', 'ordem', 'ativo', 'tem_imagem')
#     # edita ordem e ativo direto na lista, sem abrir cada banner
#     list_editable = ('ordem', 'ativo')

#     @admin.display(boolean=True, description='Imagem')
#     def tem_imagem(self, obj):
#         return bool(obj.imagem)