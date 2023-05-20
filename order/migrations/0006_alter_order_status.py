# Generated by Django 4.1.5 on 2023-05-19 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_order_apply_subtitle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, choices=[('pending', 'PENDING'), ('assigned', 'ASSIGNED'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('demo', 'Demo'), ('in_review', 'In Review'), ('canceled', 'Canceled')], max_length=30, null=True),
        ),
    ]
