# Generated by Django 4.1.5 on 2023-07-06 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload_video', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='watermark_video_file',
            field=models.FileField(blank=True, null=True, upload_to='orders/watermark_videos/'),
        ),
    ]