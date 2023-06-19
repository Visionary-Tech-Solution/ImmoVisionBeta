# Generated by Django 4.1.5 on 2023-06-17 21:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0008_alter_notification_notification_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Modified at')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Deleted at')),
                ('social_alert', models.BooleanField(default=True)),
                ('video_ready_alert', models.BooleanField(default=True)),
                ('sms_alert', models.BooleanField(default=True)),
                ('blog_post_alert', models.BooleanField(default=True)),
                ('offer_alert', models.BooleanField(default=True)),
                ('ai_document_ready_alert', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_notification_alert', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]