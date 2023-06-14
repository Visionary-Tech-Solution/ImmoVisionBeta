# Generated by Django 4.1.5 on 2023-06-14 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload_video', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='privacy_type',
            field=models.CharField(choices=[('private', 'Private'), ('public', 'Public')], default='private', max_length=30),
        ),
    ]
