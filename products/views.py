from django.contrib import messages
from django.db.models import F, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView

from .models import Banner, Categoria, Produto, CHOICE_GENERO


# Banners padrão
BANNERS_PADRAO = [
    {
        "titulo": "Promoções",
        "texto": "Peças selecionadas com desconto.",
        "link": "#promocoes",
        "botao": "Ver ofertas",
    },
    {
        "titulo": "Masculino",
        "texto": "Camisetas, calças, casacos e sapatos.",
        "link": "/departamento/masculino/",
        "botao": "Ver masculino",
    },
    {
        "titulo": "Feminino",
        "texto": "A coleção completa em um só lugar.",
        "link": "/departamento/feminino/",
        "botao": "Ver feminino",
    },
]


class HomeView(ListView):
    template_name = "products/home.html"
    context_object_name = "produtos"

    def get_queryset(self):
        return Produto.objects.filter(
            preco_promocional__isnull=False,
            preco_promocional__lt=F("preco")
        ).select_related("categoria")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        banners = Banner.objects.filter(ativo=True)
        context["banners"] = list(banners) or BANNERS_PADRAO

        return context


class DepartamentoView(ListView):
    template_name = "products/departamento.html"
    context_object_name = "produtos"

    def get_queryset(self):
        genero = self.kwargs["publico"]

        # Verifica se o gênero existe nas opções do choices
        if genero not in dict(CHOICE_GENERO):
            raise Http404("Departamento não encontrado.")

        # Masculino e feminino também recebem os produtos unissex
        filtro = Q(genero__icontains=genero)

        if genero in ["masculino", "feminino"]:
            filtro |= Q(genero__icontains="unissex")

        produtos = Produto.objects.filter(
            filtro
        ).select_related("categoria")

        # Filtro opcional por categoria
        self.categoria = None
        slug = self.kwargs.get("categoria_slug")

        if slug:
            self.categoria = get_object_or_404(Categoria, slug=slug)
            produtos = produtos.filter(categoria=self.categoria)

        return produtos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        genero = self.kwargs["publico"]

        generos = [genero]

        if genero in ["masculino", "feminino"]:
            generos.append("unissex")

        context["publico"] = genero
        context["nome_publico"] = dict(CHOICE_GENERO).get(genero)
        context["categoria"] = self.categoria

        context["categorias"] = Categoria.objects.filter(
            produtos__genero__in=generos
        ).distinct()

        return context




class BuscaView(ListView):
    template_name = "products/busca.html"
    context_object_name = "produtos"

    def get_queryset(self):
        self.search = self.request.GET.get("search", "").strip()

        produtos = Produto.objects.all()

        # Busca por texto
        if self.search:
            produtos = produtos.filter(
                Q(nome__icontains=self.search)
                | Q(descricao__icontains=self.search)
                | Q(categoria__nome__icontains=self.search)
            )

        # Filtro masculino
        if "masculino" in self.request.GET:
            produtos = produtos.filter(
                Q(genero="masculino") | Q(genero="unissex")
            )

        # Filtro feminino
        elif "feminino" in self.request.GET:
            produtos = produtos.filter(
                Q(genero="feminino") | Q(genero="unissex")
            )

        # Filtro unissex
        elif "unisex" in self.request.GET:
            produtos = produtos.filter(genero="unissex")

        # Filtro infantil
        elif "infantil" in self.request.GET:
            produtos = produtos.filter(genero="infantil")

        return produtos.select_related("categoria").distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["search"] = self.search
        context["filtro_genero"] = next(
            (
                genero for genero in
                ["masculino", "feminino", "unisex", "infantil"]
                if genero in self.request.GET
            ),
            ""
        )

        return context



class ProdutoDetailView(DetailView):
    model = Produto
    template_name = "products/produto_detalhe.html"
    context_object_name = "produto"

    def get_queryset(self):
        return Produto.objects.select_related(
            "categoria"
        ).prefetch_related("tamanhos")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Verifica se o produto possui estoque
        if not self.object.disponivel:
            messages.warning(
                request,
                f'"{self.object.nome}" está esgotado no momento.'
            )

            return redirect(
                "departamento",
                publico=self.object.genero
            )

        context = self.get_context_data(object=self.object)

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["relacionados"] = Produto.objects.filter(
            categoria=self.object.categoria
        ).exclude(
            pk=self.object.pk
        ).select_related("categoria")[:4]

        return context
















# from django.contrib import messages
# from django.db.models import F, Q
# from django.http import Http404
# from django.shortcuts import get_object_or_404, redirect
# from django.views.generic import DetailView, ListView

# from .models import Banner, Categoria, Produto

# # slides usados só quando não há nenhum banner ativo cadastrado no admin
# BANNERS_PADRAO = [
#     {
#         "titulo": "Promoções",
#         "texto": "Peças selecionadas com desconto.",
#         "link": "#promocoes",
#         "botao": "Ver ofertas",
#     },
#     {
#         "titulo": "Masculino",
#         "texto": "Camisetas, calças, casacos e sapatos.",
#         "link": "/departamento/masculino/",
#         "botao": "Ver masculino",
#     },
#     {
#         "titulo": "Feminino",
#         "texto": "A coleção completa em um só lugar.",
#         "link": "/departamento/feminino/",
#         "botao": "Ver feminino",
#     },
# ]


# class HomeView(ListView):
#     template_name = "products/home.html"
#     context_object_name = "produtos"

#     def get_queryset(self):
#         # só produtos com preço promocional menor que o preço normal
#         return Produto.objects.filter(
#             preco_promocional__isnull=False, preco_promocional__lt=F("preco")
#         ).select_related("categoria")

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # banners cadastrados no admin; se não houver, usa os padrão
#         banners = list(Banner.objects.filter(ativo=True))
#         context["banners"] = banners or BANNERS_PADRAO
#         return context


# class DepartamentoView(ListView):
#     template_name = "products/departamento.html"
#     context_object_name = "produtos"

#     def get_queryset(self):
#         # o público vem da url (/departamento/masculino/)
#         publico = self.kwargs["publico"]

#         if publico not in Produto.Publico.values:
#             raise Http404("Departamento não encontrado.")

#         produtos = Produto.objects.filter(publico=publico).select_related("categoria")

#         # a categoria é opcional: só filtra se vier na url
#         self.categoria = None
#         slug = self.kwargs.get("categoria_slug")
#         if slug:
#             self.categoria = get_object_or_404(Categoria, slug=slug)
#             produtos = produtos.filter(categoria=self.categoria)

#         return produtos

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         publico = self.kwargs["publico"]
#         context["publico"] = publico
#         context["nome_publico"] = Produto.Publico(publico).label
#         context["categoria"] = self.categoria
#         # categorias que têm produtos neste departamento
#         context["categorias"] = Categoria.objects.filter(
#             produtos__publico=publico
#         ).distinct()
#         return context


# class BuscaView(ListView):
#     template_name = "products/busca.html"
#     context_object_name = "produtos"

#     def get_queryset(self):
#         self.q = self.request.GET.get("q", "").strip()

#         if not self.q:
#             return Produto.objects.none()

#         # Q com | quer dizer "ou": basta um dos campos conter o texto
#         return Produto.objects.filter(
#             Q(nome__icontains=self.q)
#             | Q(descricao__icontains=self.q)
#             | Q(categoria__nome__icontains=self.q)
#         ).select_related("categoria")

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["q"] = self.q
#         return context


# class ProdutoDetailView(DetailView):
#     model = Produto
#     template_name = "products/produto_detalhe.html"
#     context_object_name = "produto"

#     def get_queryset(self):
#         return Produto.objects.select_related("categoria").prefetch_related("tamanhos")

#     def get(self, request, *args, **kwargs):
#         # get_object busca pelo pk da url e responde 404 se não existir
#         self.object = self.get_object()

#         # produto esgotado não abre a página de detalhes
#         if not self.object.disponivel:
#             messages.warning(request, f'"{self.object.nome}" está esgotado no momento.')
#             return redirect("departamento", publico=self.object.publico)

#         context = self.get_context_data(object=self.object)
#         return self.render_to_response(context)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # outros produtos da mesma categoria
#         context["relacionados"] = (
#             Produto.objects.filter(categoria=self.object.categoria)
#             .exclude(pk=self.object.pk)
#             .select_related("categoria")[:4]
#         )
#         return context


# # # # filtro unissex
# class FiltroUnissex(ListView):
#     queryset = Produto.objects.filter(
#         Q(publico__icontains="masculino")
#         | Q(publico__icontains="feminino")
#         | Q(publico__icontains="unissex")
#     ).select_related("categoria")

#     template_name = "products/departamento.html"
#     context_object_name = "produtos"
