# Generated by Django 4.1.5 on 2023-08-24 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_brokerprofile_realtor_profile_url_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brokerprofile',
            name='realtor_uid',
        ),
        migrations.AlterField(
            model_name='brokerprofile',
            name='realtor_profile_url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
