# Generated by Django 3.2.8 on 2021-11-15 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('file', models.FileField(upload_to='files/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('license', models.CharField(choices=[('CC BY - Mention', 'CC BY - Mention'), ('CC BY-NC - Mention - Non-commercial', 'CC BY-NC - Mention - Non-commercial')], default='CC BY - Mention', max_length=255)),
            ],
        ),
    ]
