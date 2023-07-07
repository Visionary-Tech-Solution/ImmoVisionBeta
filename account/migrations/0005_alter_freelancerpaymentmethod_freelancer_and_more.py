# Generated by Django 4.1.5 on 2023-07-07 02:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_freelancerpaymentmethod_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='freelancerpaymentmethod',
            name='freelancer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='freelancer_payment_profile', to='account.freelancerprofile'),
        ),
        migrations.AlterField(
            model_name='freelancerpaymentmethod',
            name='withdrawal_type',
            field=models.CharField(blank=True, choices=[('crypto', 'Crypto'), ('paypal', 'Paypal')], max_length=60, null=True),
        ),
    ]
