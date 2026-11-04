from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


# Opções de gênero dos produtos
CHOICE_GENERO = [
    ('masculino', 'Masculino'),
    ('feminino', 'Feminino'),
    ('unissex', 'Unissex'),
    ('infantil', 'Infantil'),
]


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Tamanho(models.Model):
    nome = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = "Tamanho"
        verbose_name_plural = "Tamanhos"
        ordering = ["id"]

    def __str__(self):
        return self.nome


class Produto(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="produtos"
    )

    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)

    genero = models.CharField(
        max_length=10,
        choices=CHOICE_GENERO,
        default='unissex'
    )

    preco = models.DecimalField(max_digits=10, decimal_places=2)

    preco_promocional = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    tamanhos = models.ManyToManyField(
        Tamanho,
        blank=True,
        related_name="produtos",
        help_text="Marque somente os tamanhos disponíveis para este produto."
    )

    estoque = models.PositiveIntegerField(default=0)

    imagem = models.ImageField(
        upload_to='produtos/',
        blank=True,
        null=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["nome"]

    @property
    def disponivel(self):
        return self.estoque > 0

    @property
    def em_promocao(self):
        return (
            self.preco_promocional is not None
            and self.preco_promocional < self.preco
        )

    @property
    def preco_atual(self):
        return self.preco_promocional if self.em_promocao else self.preco

    @property
    def desconto_percentual(self):
        if not self.em_promocao:
            return 0

        return round(
            (1 - self.preco_promocional / self.preco) * 100
        )

    def get_absolute_url(self):
        return reverse("produto_detalhe", args=[self.pk])

    def __str__(self):
        return self.nome


class Banner(models.Model):
    titulo = models.CharField(max_length=60, blank=True)
    texto = models.CharField(max_length=120, blank=True)

    imagem = models.ImageField(
        upload_to='banners/',
        blank=True,
        null=True,
        help_text=(
            "Foto deitada, de preferência 1920x1080 px e até 500 KB. "
            "Deixe o texto e o que for importante no centro, "
            "porque as pontas podem ser cortadas."
        )
    )

    imagem_celular = models.ImageField(
        "imagem para celular",
        upload_to='banners/',
        blank=True,
        null=True,
        help_text=(
            "Opcional: versão em pé para telas de celular, "
            "de preferência 800x1000 px. "
            "Sem ela, o celular usa a foto principal."
        )
    )

    link = models.CharField(
        max_length=200,
        blank=True,
        help_text=(
            "Para onde o banner leva. Ex.: "
            "/departamento/masculino/ ou #promocoes."
        )
    )

    botao = models.CharField(
        max_length=30,
        blank=True,
        help_text="Texto do botão. Deixe vazio para não mostrar botão."
    )

    ordem = models.PositiveIntegerField(
        default=0,
        help_text="Menor número aparece primeiro."
    )

    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Banner do carrossel"
        verbose_name_plural = "Banners do carrossel"
        ordering = ["ordem", "id"]

    def clean(self):
        if not self.imagem and not self.titulo:
            raise ValidationError(
                "Coloque pelo menos uma foto ou um título no banner."
            )

    def __str__(self):
        return self.titulo or f"Banner {self.pk}"









# from django.core.exceptions import ValidationError
# from django.db import models
# from django.urls import reverse


# class Categoria(models.Model):
#     nome = models.CharField(max_length=100)
#     slug = models.SlugField(unique=True)

#     class Meta:
#         verbose_name = "Categoria"
#         verbose_name_plural = "Categorias"
#         ordering = ["nome"]

#     def __str__(self):
#         return self.nome


# class Tamanho(models.Model):
#     """Tamanho de roupa (P, M, G...) ou numeração de sapato (38, 40...).

#     Fica numa tabela própria para o mesmo tamanho poder ser usado em
#     vários produtos (relação muitos-para-muitos).
#     """

#     nome = models.CharField(max_length=10, unique=True)

#     class Meta:
#         verbose_name = "Tamanho"
#         verbose_name_plural = "Tamanhos"
#         ordering = ["id"]

#     def __str__(self):
#         return self.nome


# class Produto(models.Model):
#     class Publico(models.TextChoices):
#         MASCULINO = "masculino", "Masculino"
#         FEMININO = "feminino", "Feminino"
#         UNISSEX = "unissex", "Unissex"
#         INFANTIL = "infantil", "Infantil"

#     categoria = models.ForeignKey(
#         Categoria, on_delete=models.PROTECT, related_name="produtos"
#     )
#     nome = models.CharField(max_length=200)
#     descricao = models.TextField(blank=True)
#     publico = models.CharField(
#         max_length=10, choices=Publico.choices, default=Publico.UNISSEX
#     )
#     preco = models.DecimalField(max_digits=10, decimal_places=2)
#     preco_promocional = models.DecimalField(
#         max_digits=10, decimal_places=2, blank=True, null=True
#     )
#     tamanhos = models.ManyToManyField(
#         Tamanho,
#         blank=True,
#         related_name="produtos",
#         help_text="Marque somente os tamanhos disponíveis para este produto.",
#     )
#     estoque = models.PositiveIntegerField(default=0)
#     imagem = models.ImageField(upload_to="produtos/", blank=True, null=True)
#     criado_em = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = "Produto"
#         verbose_name_plural = "Produtos"
#         ordering = ["nome"]

#     @property
#     def disponivel(self):
#         # Produto com estoque zerado fica "esgotado" na loja.
#         return self.estoque > 0

#     @property
#     def em_promocao(self):
#         return (
#             self.preco_promocional is not None and self.preco_promocional < self.preco
#         )

#     @property
#     def preco_atual(self):
#         if self.em_promocao:
#             return self.preco_promocional
#         return self.preco

#     @property
#     def desconto_percentual(self):
#         if not self.em_promocao:
#             return 0
#         return round((1 - self.preco_promocional / self.preco) * 100)

#     def get_absolute_url(self):
#         # Gera /produto/<id>/ a partir do nome da rota 'produto_detalhe'.
#         return reverse("produto_detalhe", args=[self.pk])

#     def __str__(self):
#         return self.nome

# class Banner(models.Model):
#     """Slide do carrossel da página inicial (cadastrado pelo admin)."""

#     # título, texto, botão e link são opcionais: a foto pode já ter tudo escrito
#     titulo = models.CharField(max_length=60, blank=True)
#     texto = models.CharField(max_length=120, blank=True)
#     imagem = models.ImageField(
#         upload_to="banners/",
#         blank=True,
#         null=True,
#         help_text="Foto deitada, de preferência 1920x1080 px e até 500 KB. "
#         "Deixe o texto e o que for importante no centro, porque as pontas podem ser cortadas.",
#     )
#     imagem_celular = models.ImageField(
#         "imagem para celular",
#         upload_to="banners/",
#         blank=True,
#         null=True,
#         help_text="Opcional: versão em pé para telas de celular, de preferência 800x1000 px. "
#         "Sem ela, o celular usa a foto principal.",
#     )
#     link = models.CharField(
#         max_length=200,
#         blank=True,
#         help_text="Para onde o banner leva. Ex.: /departamento/masculino/ ou #promocoes. Deixe vazio se não quiser link.",
#     )
#     botao = models.CharField(
#         max_length=30,
#         blank=True,
#         help_text="Texto do botão. Deixe vazio para não mostrar botão (a foto inteira vira o link).",
#     )
#     ordem = models.PositiveIntegerField(
#         default=0, help_text="Menor número aparece primeiro."
#     )
#     ativo = models.BooleanField(default=True)

#     class Meta:
#         verbose_name = "Banner do carrossel"
#         verbose_name_plural = "Banners do carrossel"
#         ordering = ["ordem", "id"]

#     def clean(self):
#         # sem foto e sem título o slide ficaria vazio
#         if not self.imagem and not self.titulo:
#             raise ValidationError("Coloque pelo menos uma foto ou um título no banner.")

#     def __str__(self):
#         return self.titulo or f"Banner {self.pk}"
