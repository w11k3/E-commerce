from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario

    list_display = (
        'email',
        'nome',
        'sobrenome',
        'is_active',
        'is_staff',
        'is_superuser',
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('email', 'nome', 'sobrenome', 'username')
    ordering = ('email',)
    list_per_page = 20
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Dados pessoais', {
            'fields': ('nome', 'sobrenome', 'username')
        }),
        ('Permissões', {
            'fields': (
                'is_active',   #indica se a conta está ativa.
                'is_staff',    #permite entrar no painel administrativo, desde que a conta esteja ativa.
                'is_superuser',  #concede todas as permissões, sem precisar atribuí-las individualmente.
                'groups',       #grupos dos quais o usuário participa.
                'user_permissions',   #permissões específicas daquele usuário.
            )
        }),
        ('Datas importantes', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'nome',
                'sobrenome',
                'password1',
                'password2',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )
