# Generated by Django 4.1.4 on 2025-02-10 14:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0069_remove_elemente_bestellungen_adresse_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LieferantenBestellungen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('kunden_nr', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Lieferanten-Bestellung',
                'verbose_name_plural': 'Lieferanten-Bestellungen',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='LieferantenStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_updates', to='store.lieferantenbestellungen')),
            ],
        ),
        migrations.CreateModel(
            name='LieferantenBestellungenArtikel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('anzahl', models.PositiveIntegerField(verbose_name='Anzahl')),
                ('artikel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lieferanten_artikel', to='store.artikel')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='artikel_bestellungen', to='store.lieferantenbestellungen')),
            ],
        ),
        migrations.AddField(
            model_name='lieferantenbestellungen',
            name='status',
            field=models.ManyToManyField(blank=True, related_name='bestellungen', to='store.lieferantenstatus'),
        ),
    ]
