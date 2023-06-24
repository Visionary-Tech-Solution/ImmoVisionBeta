# Generated by Django 4.1.5 on 2023-06-24 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0012_alter_discountcode_code_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('unpaid', 'Unpaid'), ('pending', 'PENDING'), ('assigned', 'ASSIGNED'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('demo', 'Demo'), ('in_review', 'In Review'), ('canceled', 'Canceled')], max_length=80),
        ),
    ]
