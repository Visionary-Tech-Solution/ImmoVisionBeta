# Generated by Django 4.1.5 on 2023-05-22 02:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_delete_admin_delete_broker_delete_freelancer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(max_length=100, unique=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='user',
            name='type',
            field=models.CharField(choices=[('UNSPECIFIED', 'Unspecified'), ('BROKER', 'Broker'), ('FREELANCER', 'Freelancer'), ('ADMIN', 'Admin')], default='BROKER', max_length=80),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=80, unique=True, verbose_name='Username'),
        ),
    ]
