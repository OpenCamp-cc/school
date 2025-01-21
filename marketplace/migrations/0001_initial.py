# Generated by Django 5.1.3 on 2024-11-12 20:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('languages', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('bio', models.TextField()),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='student_profiles')),
                ('rating', models.FloatField(default=0.0)),
                ('rating_count', models.IntegerField(default=0)),
                ('rating_sum', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TeacherProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('bio', models.TextField()),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='teacher_profiles')),
                ('rating', models.FloatField(default=0.0)),
                ('rating_count', models.IntegerField(default=0)),
                ('rating_sum', models.IntegerField(default=0)),
                ('title', models.CharField(max_length=255)),
                ('tagline', models.CharField(max_length=255)),
                ('is_certified', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TeacherLanguageProficiency',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('proficiency', models.CharField(max_length=255)),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='languages.language')),
                ('teacher_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='language_proficiencies', to='marketplace.teacherprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TeacherCertificate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('certificate_name', models.CharField(max_length=255)),
                ('year_of_issue', models.IntegerField()),
                ('certificate', models.ImageField(upload_to='teacher_certificates')),
                ('teacher_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificates', to='marketplace.teacherprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
