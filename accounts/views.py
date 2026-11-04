from django.shortcuts import render, redirect
from .forms import CadastroForm


def cadastro_view(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CadastroForm()

    return render(request, 'accounts/cadastro.html', {
        'form': form
    })