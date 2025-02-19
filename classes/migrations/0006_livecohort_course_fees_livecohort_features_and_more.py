# Generated by Django 5.1.5 on 2025-02-19 19:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0005_livecohort_end_date_livecohort_start_date_and_more'),
        ('quizzes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='livecohort',
            name='course_fees',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='livecohort',
            name='features',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='livecohort',
            name='key_topics',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='livecohort',
            name='requirements',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='livecohort',
            name='schedule',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='livecohortassignment',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='assignments/'),
        ),
        migrations.AddField(
            model_name='livecohortassignment',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='livecohortassignment',
            name='external_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='livecohortassignment',
            name='submission_optional',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='livecohortassignmentsubmission',
            name='comments',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='livecohortassignment',
            name='cohort',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='classes.livecohort'),
        ),
        migrations.AlterField(
            model_name='livecohortassignmentsubmission',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='submissions/'),
        ),
        migrations.CreateModel(
            name='LiveCohortQuiz',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('due_date', models.DateTimeField()),
                ('is_required', models.BooleanField(default=True)),
                ('points', models.PositiveIntegerField(default=0)),
                ('cohort', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cohort_quizzes', to='classes.livecohort')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quizzes.quiz')),
            ],
            options={
                'unique_together': {('cohort', 'quiz')},
            },
        ),
        migrations.AddField(
            model_name='livecohort',
            name='quizzes',
            field=models.ManyToManyField(through='classes.LiveCohortQuiz', to='quizzes.quiz'),
        ),
    ]
