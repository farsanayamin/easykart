# Generated by Django 3.1 on 2024-03-15 08:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_remove_account_referral_link'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='is_verified',
        ),
        migrations.RemoveField(
            model_name='account',
            name='profile',
        ),
    ]