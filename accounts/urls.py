from django.urls import path
from django.contrib.auth import views as auth_views

from .views import cadastro_view


urlpatterns = [
    path('cadastro/', cadastro_view, name='cadastro'),

    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='accounts/login.html',
            next_page='home',
        ),
        name='login',
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(
            next_page='home',
        ),
        name='logout',
    ),
]