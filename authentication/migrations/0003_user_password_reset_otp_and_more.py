# Generated by Django 4.1.5 on 2023-06-24 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_user_password_reset_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='password_reset_OTP',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='password_reset_token',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
