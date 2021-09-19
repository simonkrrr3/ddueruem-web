# Generated by Django 3.2.4 on 2021-08-06 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dockerManager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dockerprocess',
            name='library',
            field=models.CharField(choices=[('buddy', 'BuDDy'), ('cudd', 'CUDD')], default='buddy', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dockerprocess',
            name='resources',
            field=models.CharField(choices=[('4-1', '4 GB RAM, 1 CPU core'), ('32-1', '32 GB RAM, 1 CPU core'), ('32-16', '32 GB RAM, 16 CPU cores')], default='4-1', max_length=20),
        ),
    ]
