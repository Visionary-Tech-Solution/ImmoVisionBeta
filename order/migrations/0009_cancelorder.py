# Generated by Django 4.1.5 on 2023-06-14 12:38

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_brokerprofile_total_orders'),
        ('order', '0008_alter_order_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='CancelOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Modified at')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Deleted at')),
                ('cancel_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(max_length=600)),
                ('details', models.TextField()),
                ('cancel_requ_sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.profile')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.order')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
