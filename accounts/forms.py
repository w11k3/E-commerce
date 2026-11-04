from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class CadastroForm(UserCreationForm):
    nome = forms.CharField(
        label='Nome',
        max_length=100
    )

    sobrenome = forms.CharField(
        label='Sobrenome',
        max_length=100
    )

    email = forms.EmailField(
        label='E-mail'
    )

    class Meta:
        model = Usuario
        # sem username aqui: o login é feito pelo e-mail
        fields = [
            'nome',
            'sobrenome',
            'email',
        ]

    def clean_email(self):
        email = self.cleaned_data['email'].strip()

        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'Este e-mail já está cadastrado. Entre na sua conta.'
            )

        # o username aceita no máximo 150 caracteres e vai receber o e-mail
        if len(email) > 150:
            raise forms.ValidationError('E-mail muito longo.')

        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)

        # o model Usuario herda de AbstractUser e ainda exige um username
        # único, então guardamos o próprio e-mail nele
        usuario.username = usuario.email

        if commit:
            usuario.save()

        return usuario