# Generated by Django 4.1.5 on 2023-06-17 19:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('upload_video', '0002_alter_video_privacy_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='subtitle',
        ),
    ]
