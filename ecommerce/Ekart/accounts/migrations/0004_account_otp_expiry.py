# Generated by Django 3.1 on 2024-02-28 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20240227_2032'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='otp_expiry',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
