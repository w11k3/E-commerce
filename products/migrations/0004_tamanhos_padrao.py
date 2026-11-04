from django.db import migrations

# Tamanhos criados automaticamente: roupas e numerações de sapato.
TAMANHOS = ['P', 'M', 'G', 'GG'] + [str(n) for n in range(34, 45)]


def criar_tamanhos(apps, schema_editor):
    Tamanho = apps.get_model('products', 'Tamanho')
    for nome in TAMANHOS:
        Tamanho.objects.get_or_create(nome=nome)


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_tamanho_produto_tamanhos'),
    ]

    operations = [
        migrations.RunPython(criar_tamanhos, migrations.RunPython.noop),
    ]