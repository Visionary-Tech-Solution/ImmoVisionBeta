# Generated by Django 4.1.5 on 2023-06-25 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0015_order_payment_method_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]