# Generated by Django 4.1.5 on 2023-06-19 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_alter_freelancerprofile_pending_earn_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='stripe_customer_id',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
    ]