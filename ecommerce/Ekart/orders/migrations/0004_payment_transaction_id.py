# Generated by Django 3.1 on 2024-04-27 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20240427_2131'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]