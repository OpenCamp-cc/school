# Generated by Django 5.1.6 on 2025-03-10 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0007_remove_livecohortquiz_points_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='livecohortsession',
            name='video_recording_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='livecohortsession',
            name='video_recording_notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
