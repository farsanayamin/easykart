# Generated by Django 3.1 on 2024-03-05 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20240301_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='last_otp_attempt',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='otp_attempts',
            field=models.IntegerField(default=0),
        ),
    ]