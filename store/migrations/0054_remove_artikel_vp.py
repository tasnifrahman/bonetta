# Generated by Django 4.1.4 on 2024-12-11 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0053_artikel_lieferantenartikel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artikel',
            name='vp',
        ),
    ]
