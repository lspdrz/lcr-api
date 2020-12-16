# Generated by Django 3.1.4 on 2020-12-16 10:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cr_id', models.CharField(max_length=128, unique=True)),
                ('cr_sub_id', models.IntegerField()),
                ('source_url', models.CharField(max_length=255, unique=True)),
                ('registration_number', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('additional_name', models.CharField(max_length=255)),
                ('governorate', models.IntegerField(choices=[(1, 'Beirut'), (2, 'Mount Lebanon'), (3, 'North Lebanon'), (4, 'Bekaa'), (5, 'South Lebanon'), (6, 'Nabatieh')])),
                ('registration_date', models.DateTimeField()),
                ('record_type', models.CharField(max_length=255)),
                ('company_status', models.CharField(max_length=255)),
                ('company_duration', models.CharField(max_length=255)),
                ('legal_form', models.CharField(max_length=255)),
                ('capital', models.DecimalField(decimal_places=2, max_digits=15)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('missing_personnel_data', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ScrapeError',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cr_id', models.CharField(max_length=128, unique=True)),
                ('model_type', models.CharField(choices=[('CO', 'Company'), ('PE', 'Person'), ('UK', 'Unknown')], default='UK', max_length=2)),
                ('error_message', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('nationality', models.CharField(max_length=128)),
                ('relationship', models.CharField(max_length=128)),
                ('stock', models.IntegerField()),
                ('quota', models.IntegerField()),
                ('ratio', models.IntegerField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company', to='api.company')),
            ],
        ),
        migrations.AddIndex(
            model_name='company',
            index=models.Index(fields=['name'], name='company_name_idx'),
        ),
        migrations.AddIndex(
            model_name='person',
            index=models.Index(fields=['name'], name='person_name_idx'),
        ),
    ]
