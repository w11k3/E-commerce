from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .models import ItemCarrinho
from products.models import Produto, Tamanho

# parcelamento sem juros: quantidades oferecidas e valor mínimo de cada parcela
PARCELAS_OFERECIDAS = [2, 3, 6, 10, 12]
VALOR_MINIMO_PARCELA = Decimal('20.00')


class EstoqueInsuficiente(Exception):
    # usada para cancelar a compra quando falta estoque
    pass


def _unidades_no_carrinho(usuario, produto):
    # o estoque é do produto (não do tamanho), então somamos todos os tamanhos
    total = ItemCarrinho.objects.filter(
        usuario=usuario, produto=produto
    ).aggregate(total=Sum('quantidade'))['total']
    return total or 0


def _ler_formulario(request, produto, considerar_carrinho=True):
    # lê e valida o tamanho e a quantidade enviados pela página do produto
    # retorna (tamanho, quantidade, erro); o erro vem como texto
    try:
        quantidade = int(request.POST.get('quantidade', 1))
    except ValueError:
        quantidade = 0

    if not produto.disponivel:
        return None, 0, 'Este produto está esgotado.'

    # quantas unidades ainda podem ser adicionadas:
    # estoque menos o que a pessoa já tem no carrinho
    restante = produto.estoque
    if considerar_carrinho:
        restante -= _unidades_no_carrinho(request.user, produto)

    if restante <= 0:
        return None, 0, 'Você já tem no carrinho todas as unidades disponíveis deste produto.'

    if quantidade < 1 or quantidade > restante:
        return None, 0, f'Só é possível adicionar de 1 a {restante} unidade(s).'

    tamanho = None
    if produto.tamanhos.exists():
        tamanho_id = request.POST.get('tamanho', '')
        if tamanho_id.isdigit():
            # só aceita tamanhos que pertencem a este produto
            tamanho = produto.tamanhos.filter(pk=tamanho_id).first()
        if tamanho is None:
            return None, 0, 'Escolha um tamanho antes de continuar.'

    return tamanho, quantidade, None


def _opcoes_parcelas(total):
    # valor de cada parcela, sem juros, só para as parcelas que não ficam
    # abaixo do valor mínimo
    opcoes = []
    for numero in PARCELAS_OFERECIDAS:
        valor = (total / numero).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if valor >= VALOR_MINIMO_PARCELA:
            opcoes.append({'numero': numero, 'valor': valor})
    return opcoes


def _ler_pagamento(dados, total):
    # confere a forma de pagamento escolhida no checkout
    # retorna um dicionário, ou None se o que veio do formulário não vale
    if dados.get('pagamento') == 'avista':
        return {'tipo': 'avista'}

    if dados.get('pagamento') == 'parcelado':
        for opcao in _opcoes_parcelas(total):
            if str(opcao['numero']) == dados.get('parcelas'):
                return {'tipo': 'parcelado', **opcao}

    return None


def _ir_para_login(produto):
    # depois de entrar, a pessoa volta para a página do produto
    return redirect(f"{reverse('login')}?next={produto.get_absolute_url()}")


def adicionar_carrinho(request, produto_id):
    # botão "Adicionar ao carrinho" da página do produto
    if request.method != 'POST':
        return redirect('home')

    produto = get_object_or_404(Produto, id=produto_id)

    if not request.user.is_authenticated:
        return _ir_para_login(produto)

    tamanho, quantidade, erro = _ler_formulario(request, produto)
    if erro:
        messages.error(request, erro)
        return redirect(produto.get_absolute_url())

    # o mesmo produto em tamanhos diferentes vira linhas diferentes
    item, criado = ItemCarrinho.objects.get_or_create(
        usuario=request.user,
        produto=produto,
        tamanho=tamanho,
        defaults={'quantidade': quantidade},
    )
    if not criado:
        item.quantidade += quantidade
        item.save()

    messages.success(request, 'Produto adicionado ao carrinho.')
    return redirect(produto.get_absolute_url())


def comprar_agora(request, produto_id):
    # botão "Comprar agora": vai direto ao checkout, sem passar pelo carrinho
    if request.method != 'POST':
        return redirect('home')

    produto = get_object_or_404(Produto, id=produto_id)

    if not request.user.is_authenticated:
        return _ir_para_login(produto)

    tamanho, quantidade, erro = _ler_formulario(
        request, produto, considerar_carrinho=False
    )
    if erro:
        messages.error(request, erro)
        return redirect(produto.get_absolute_url())

    # guarda na sessão só o produto escolhido para essa compra
    request.session['compra_direta'] = {
        'produto_id': produto.id,
        'tamanho_id': tamanho.id if tamanho else None,
        'quantidade': quantidade,
    }
    return redirect('checkout')


@login_required
def ver_carrinho(request):
    # ao abrir o carrinho, a compra direta é descartada
    request.session.pop('compra_direta', None)

    itens = ItemCarrinho.objects.filter(
        usuario=request.user
    ).select_related('produto__categoria', 'tamanho')

    total = 0
    tem_problema = False
    for item in itens:
        # o preço vem sempre do banco (já considera a promoção)
        item.subtotal = item.produto.preco_atual * item.quantidade
        total += item.subtotal
        # avisa se o estoque diminuiu depois que o item entrou no carrinho
        item.sem_estoque = item.quantidade > item.produto.estoque
        tem_problema = tem_problema or item.sem_estoque

    return render(request, 'cart/carrinho.html', {
        'itens': itens,
        'total': total,
        'tem_problema': tem_problema,
    })


@login_required
def alterar_quantidade(request, item_id, acao):
    if request.method == 'POST':
        item = get_object_or_404(ItemCarrinho, id=item_id, usuario=request.user)

        if acao == 'aumentar':
            # não deixa passar do estoque (somando todos os tamanhos)
            if _unidades_no_carrinho(request.user, item.produto) < item.produto.estoque:
                item.quantidade += 1
                item.save()
            else:
                messages.warning(request, 'Você chegou ao limite de estoque deste produto.')

        elif acao == 'diminuir' and item.quantidade > 1:
            item.quantidade -= 1
            item.save()

    return redirect('carrinho')


@login_required
def remover_carrinho(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(ItemCarrinho, id=item_id, usuario=request.user)
        item.delete()

    return redirect('carrinho')


def _linhas_da_compra(request):
    # monta a lista do que está sendo comprado (compra direta ou carrinho)
    # cada linha é um dicionário com produto, tamanho e quantidade
    compra_direta = request.session.get('compra_direta')

    if compra_direta:
        produto = Produto.objects.filter(id=compra_direta['produto_id']).first()
        if produto is None:
            return []
        tamanho = Tamanho.objects.filter(pk=compra_direta.get('tamanho_id')).first()
        return [{
            'produto': produto,
            'tamanho': tamanho,
            'quantidade': max(1, int(compra_direta.get('quantidade', 1))),
        }]

    itens = ItemCarrinho.objects.filter(
        usuario=request.user
    ).select_related('produto', 'tamanho')
    return [
        {'produto': i.produto, 'tamanho': i.tamanho, 'quantidade': i.quantidade}
        for i in itens
    ]


@login_required
def checkout(request):
    # tela de endereço e pagamento, com o resumo do pedido
    linhas = _linhas_da_compra(request)

    if not linhas:
        return redirect('carrinho')

    total = 0
    for linha in linhas:
        if linha['quantidade'] > linha['produto'].estoque:
            messages.error(
                request,
                f'"{linha["produto"].nome}" não tem estoque suficiente. Ajuste a quantidade.'
            )
            return redirect('carrinho')
        linha['subtotal'] = linha['produto'].preco_atual * linha['quantidade']
        total += linha['subtotal']

    return render(request, 'cart/checkout.html', {
        'linhas': linhas,
        'total': total,
        'parcelas': _opcoes_parcelas(total),
        'valor_minimo_parcela': VALOR_MINIMO_PARCELA,
    })


@login_required
def finalizar_compra(request):
    # A finalização só pode acontecer por POST.
    if request.method != "POST":
        return redirect("checkout")

    linhas = _linhas_da_compra(request)

    if not linhas:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect("carrinho")

    # Valida o pagamento com os preços atuais do banco.
    total_previsto = sum(
        linha["produto"].preco_atual * linha["quantidade"]
        for linha in linhas
    )

    pagamento = _ler_pagamento(request.POST, total_previsto)

    if pagamento is None:
        messages.error(request, "Escolha uma forma de pagamento válida.")
        return redirect("checkout")

    resumo = []
    total = Decimal("0.00")

    try:
        with transaction.atomic():
            for linha in linhas:
                # Busca novamente o produto no banco dentro da transação.
                produto = (
                    Produto.objects
                    .select_for_update()
                    .get(pk=linha["produto"].pk)
                )

                quantidade = linha["quantidade"]

                if quantidade < 1:
                    raise EstoqueInsuficiente(produto.nome)

                if produto.estoque < quantidade:
                    raise EstoqueInsuficiente(produto.nome)

                # Confere que o tamanho escolhido realmente pertence
                # ao produto, caso ele tenha tamanhos cadastrados.
                tamanho = linha["tamanho"]

                if produto.tamanhos.exists():
                    if (
                        tamanho is None
                        or not produto.tamanhos.filter(
                            pk=tamanho.pk
                        ).exists()
                    ):
                        raise EstoqueInsuficiente(
                            f"tamanho inválido para {produto.nome}"
                        )

                subtotal = produto.preco_atual * quantidade

                produto.estoque -= quantidade
                produto.save(update_fields=["estoque"])

                total += subtotal

                resumo.append({
                    "nome": produto.nome,
                    "tamanho_nome": tamanho.nome if tamanho else "",
                    "quantidade": quantidade,
                    "subtotal": str(subtotal),
                })

            # Só esvazia o carrinho se a compra veio do carrinho.
            # "Comprar agora" usa a sessão e não deve apagar outros itens.
            if not request.session.get("compra_direta"):
                ItemCarrinho.objects.filter(
                    usuario=request.user
                ).delete()

    except EstoqueInsuficiente as erro:
        messages.error(
            request,
            f"Não foi possível concluir a compra: {erro}. "
            "Confira o estoque e tente novamente."
        )
        return redirect("carrinho")

    # Guarda apenas os dados necessários para mostrar a confirmação.
    # Não é um pedido persistido no banco.
    pagamento_confirmacao = {
        "tipo": pagamento["tipo"],
    }

    if pagamento["tipo"] == "parcelado":
        pagamento_confirmacao["numero"] = pagamento["numero"]
        pagamento_confirmacao["valor"] = str(pagamento["valor"])

    request.session["compra_finalizada"] = {
        "resumo": resumo,
        "total": str(total),
        "pagamento": pagamento_confirmacao,
        "nome": request.POST.get("nome", "").strip(),
        "cidade": request.POST.get("cidade", "").strip(),
        "estado": request.POST.get("estado", "").strip().upper(),
    }

    # Limpa os dados da compra direta e redireciona para uma página GET.
    request.session.pop("compra_direta", None)

    return redirect("compra_finalizada")


@login_required
def compra_finalizada(request):
    # Exibe a confirmação guardada temporariamente na sessão.
    dados = request.session.get("compra_finalizada")

    if not dados:
        messages.info(request, "Não há uma compra recente para exibir.")
        return redirect("home")

    return render(request, "cart/finalizado.html", dados)