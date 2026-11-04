from django.db.models import Sum


def loja(request):
    """Disponibiliza em TODOS os templates a quantidade de itens do carrinho."""
    quantidade = 0

    if request.user.is_authenticated:
        resultado = request.user.itemcarrinho_set.aggregate(
            total=Sum('quantidade')
        )
        quantidade = resultado['total'] or 0

    return {'carrinho_quantidade': quantidade}