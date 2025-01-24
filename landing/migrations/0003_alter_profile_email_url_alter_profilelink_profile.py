# Generated by Django 5.1.5 on 2025-01-24 03:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0002_alter_profilecategory_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='email_url',
            field=models.EmailField(blank=True, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='profilelink',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='landing.profile'),
        ),
    ]
