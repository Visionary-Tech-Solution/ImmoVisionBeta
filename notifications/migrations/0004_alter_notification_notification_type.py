# Generated by Django 4.1.5 on 2023-06-10 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_alter_notification_desc_alter_notification_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(blank=True, choices=[('order', 'Order'), ('borker', 'Broker')], max_length=60, null=True),
        ),
    ]