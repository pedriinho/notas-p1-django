# Generated by Django 4.2 on 2023-04-21 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nota', '0008_dataattnota'),
    ]

    operations = [
        migrations.CreateModel(
            name='Turma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turma', models.CharField(max_length=4)),
                ('id_prova1', models.IntegerField(default=0)),
                ('id_prova2', models.IntegerField(default=0)),
                ('id_prova3', models.IntegerField(default=0)),
                ('id_prova4', models.IntegerField(default=0)),
                ('id_lista1', models.IntegerField(default=0)),
                ('id_lista2', models.IntegerField(default=0)),
                ('id_lista3', models.IntegerField(default=0)),
                ('id_lista4', models.IntegerField(default=0)),
                ('id_lista5', models.IntegerField(default=0)),
                ('id_lista6', models.IntegerField(default=0)),
                ('id_lista7', models.IntegerField(default=0)),
                ('id_lista8', models.IntegerField(default=0)),
            ],
        ),
    ]
