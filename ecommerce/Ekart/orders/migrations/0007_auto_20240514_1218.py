# Generated by Django 3.1 on 2024-05-14 06:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0006_auto_20240506_0857'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='amount_paid',
            field=models.CharField(default=0, max_length=100),
        ),
        migrations.AddField(
            model_name='payment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_id',
            field=models.CharField(default=0, max_length=100),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='status',
            field=models.CharField(default='New', max_length=100),
        ),
        migrations.AddField(
            model_name='payment',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Accepted', 'Accepted'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled'), ('Return Requested', 'Return Requested'), ('Return Accepted', 'Return Accepted'), ('Return Denied', 'Return Denied')], default='New', max_length=100),
        ),
    ]
