# Generated by Django 3.1.4 on 2020-12-18 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapeerror',
            name='error_message',
            field=models.TextField(),
        ),
    ]
