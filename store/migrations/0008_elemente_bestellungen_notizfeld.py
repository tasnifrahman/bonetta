# Generated by Django 5.1.6 on 2025-04-15 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_lieferanten_our_kundennumber_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='elemente_bestellungen',
            name='notizfeld',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Notizfeld'),
        ),
    ]
