# Generated by Django 4.1.5 on 2023-07-07 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_alter_freelancerpaymentmethod_paypal_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='freelancerprofile',
            name='total_income',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]