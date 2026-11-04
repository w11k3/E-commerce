from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import Usuario
from products.models import Categoria, Produto
from cart.models import ItemCarrinho


class FinalizarCompraTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="cliente@exemplo.com",
            email="cliente@exemplo.com",
            password="SenhaTeste123!",
            nome="Cliente",
            sobrenome="Teste",
        )

        self.categoria = Categoria.objects.create(
            nome="Camisetas",
            slug="camisetas",
        )

        self.produto = Produto.objects.create(
            categoria=self.categoria,
            nome="Camiseta de teste",
            descricao="Produto usado nos testes.",
            preco=Decimal("100.00"),
            estoque=5,
        )

        self.item = ItemCarrinho.objects.create(
            usuario=self.usuario,
            produto=self.produto,
            quantidade=2,
        )

        self.client.force_login(self.usuario)

    def test_finalizar_compra_baixa_estoque_e_esvazia_carrinho(self):
        resposta = self.client.post(
            reverse("finalizar_compra"),
            {
                "pagamento": "avista",
                "nome": "Cliente Teste",
                "cidade": "Campo Grande",
                "estado": "MS",
            },
        )

        self.assertRedirects(
            resposta,
            reverse("compra_finalizada"),
            fetch_redirect_response=False,
        )

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.estoque, 3)
        self.assertFalse(
            ItemCarrinho.objects.filter(
                usuario=self.usuario
            ).exists()
        )

    def test_atualizar_confirmacao_nao_baixa_estoque_novamente(self):
        self.client.post(
            reverse("finalizar_compra"),
            {
                "pagamento": "avista",
                "nome": "Cliente Teste",
                "cidade": "Campo Grande",
                "estado": "MS",
            },
        )

        resposta = self.client.get(reverse("compra_finalizada"))

        self.assertEqual(resposta.status_code, 200)

        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque, 3)

    def test_get_nao_finaliza_compra(self):
        resposta = self.client.get(reverse("finalizar_compra"))

        self.assertRedirects(
            resposta,
            reverse("checkout"),
            fetch_redirect_response=False,
        )

        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque, 5)
        self.assertTrue(
            ItemCarrinho.objects.filter(pk=self.item.pk).exists()
        )