# Generated by Django 3.1 on 2024-05-05 07:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('addressbook', '0001_initial'),
        ('orders', '0005_auto_20240505_1314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='address',
            field=models.ForeignKey(default='adresssone', on_delete=django.db.models.deletion.CASCADE, to='addressbook.useraddressbook'),
        ),
    ]
