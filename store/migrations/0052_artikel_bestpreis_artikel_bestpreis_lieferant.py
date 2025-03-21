# Generated by Django 4.1.4 on 2024-12-11 07:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0051_artikel_preiscode'),
    ]

    operations = [
        migrations.AddField(
            model_name='artikel',
            name='bestpreis',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='artikel',
            name='bestpreis_lieferant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='artikel_lieferanten_bestpreis', to='store.lieferanten'),
        ),
    ]
