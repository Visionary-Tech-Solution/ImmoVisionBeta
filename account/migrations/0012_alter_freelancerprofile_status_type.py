# Generated by Django 4.1.5 on 2023-05-14 00:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_alter_brokerprofile_deleted_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='freelancerprofile',
            name='status_type',
            field=models.CharField(choices=[('active', 'Active'), ('suspended', 'Suspended'), ('not_available', 'Not available'), ('terminated', 'Terminated')], default=('active', 'Active'), max_length=30),
        ),
    ]
