# Generated by Django 3.1 on 2024-05-05 07:44

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('addressbook', '0001_initial'),
        ('orders', '0004_payment_transaction_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproduct',
            name='address',
            field=models.ForeignKey(default=django.utils.timezone.now, on_delete=django.db.models.deletion.CASCADE, to='addressbook.useraddressbook'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='expected',
            field=models.DateField(null=True),
        ),
    ]
