# Generated by Django 4.1.5 on 2023-06-09 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrokersFileCSV',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Modified at')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Deleted at')),
                ('file', models.FileField(upload_to='broker_dataset_files')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='brokerprofile',
            name='language',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
