# Generated by Django 3.1 on 2024-03-15 06:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_auto_20240315_1211'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='referral_link',
        ),
    ]