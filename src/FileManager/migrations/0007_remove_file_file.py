# Generated by Django 3.2.4 on 2021-07-23 01:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FileManager', '0006_auto_20210723_0234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='file',
        ),
    ]
