# Generated by Django 3.1 on 2024-04-01 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_auto_20240318_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_listed',
            field=models.BooleanField(default=True),
        ),
    ]
