# Generated by Django 5.1.5 on 2025-02-19 19:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0006_livecohort_course_fees_livecohort_features_and_more'),
        ('quizzes', '0002_remove_quizattempt_attempt_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='livecohortquiz',
            name='points',
        ),
        migrations.CreateModel(
            name='LiveCohortQuizSubmission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('submission_time', models.DateTimeField(auto_now_add=True)),
                ('cohort_quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='classes.livecohortquiz')),
                ('quiz_attempt', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cohort_submission', to='quizzes.quizattempt')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
