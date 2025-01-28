from datetime import datetime, timedelta
from typing import List

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from db.models import BaseModel, CreatedUpdatedMixin
from quizzes.models import Quiz
from users.models import User


class LiveCohort(BaseModel, CreatedUpdatedMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    max_students = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(99), MinValueValidator(1)]
    )

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # price for the class, in USD only for now
    price = models.DecimalField(max_digits=6, decimal_places=2)

    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cohorts_taught'
    )
    students = models.ManyToManyField(User, through='LiveCohortRegistration')
    sessions: models.QuerySet['LiveCohortSession']
    assignments: models.QuerySet['LiveCohortAssignment']
    quizzes = models.ManyToManyField('quizzes.Quiz', through='LiveCohortQuiz')

    upcoming_assignments: List['LiveCohortAssignment']
    upcoming_sessions: List['LiveCohortSession']
    upcoming_quizzes: List['Quiz']
    progress: int | None = None

    def course_progress(self):
        if not self.progress:
            # Check today's date against end date to track progress
            if self.start_date is None or self.end_date is None:
                return None

            total_days = (self.end_date - self.start_date).days
            days_passed = (timezone.now() - self.start_date).days
            self.progress = int(days_passed / total_days)

        return self.progress

    def __str__(self):
        return self.name


class LiveCohortSessionManager(models.Manager):
    def create_weekly_recurring_sessions(
        self,
        cohort: LiveCohort,
        start_time: datetime,
        end_time: datetime,
        sessions_count: int,
    ):
        sessions: List[LiveCohortSession] = []
        for i in range(sessions_count):
            session = LiveCohortSession(
                cohort=cohort,
                name=f'{cohort.name}: Week {i + 1}',
                start_time=start_time,
                end_time=end_time,
            )
            sessions.append(session)
            start_time = start_time + timedelta(weeks=1)
            end_time = end_time + timedelta(weeks=1)

        self.bulk_create(sessions)


class LiveCohortSession(BaseModel, CreatedUpdatedMixin):
    objects: LiveCohortSessionManager = LiveCohortSessionManager()
    cohort = models.ForeignKey(
        LiveCohort, on_delete=models.CASCADE, related_name='sessions'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    meeting_url = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f'{self.name} - {self.cohort} - {self.start_time} ~ {self.end_time}'


class LiveCohortRegistration(BaseModel):
    cohort = models.ForeignKey(LiveCohort, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    registration_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student} - {self.cohort}'


class LiveCohortAssignment(BaseModel, CreatedUpdatedMixin):
    cohort = models.ForeignKey(
        LiveCohort, on_delete=models.CASCADE, related_name='assignments'
    )
    name = models.CharField(max_length=255)
    graded = models.BooleanField(default=False)
    due_date = models.DateTimeField()

    description = models.TextField(null=True, blank=True)

    attachment = models.FileField(upload_to='assignments/', blank=True, null=True)
    external_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f'{self.name} - {self.cohort}'


class LiveCohortAssignmentSubmission(BaseModel, CreatedUpdatedMixin):
    assignment = models.ForeignKey(
        LiveCohortAssignment, on_delete=models.CASCADE, related_name='submissions'
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.TextField(null=True, blank=True)
    submitted = models.BooleanField(default=False)
    submission_time = models.DateTimeField(auto_now_add=True)

    feedback = models.TextField(blank=True)
    score = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(100), MinValueValidator(0)],
        default=0,
    )
    attachment = models.FileField(upload_to='submissions/', blank=True, null=True)

    def __str__(self):
        return f'{self.student} - {self.assignment}'


class LiveCohortQuiz(BaseModel, CreatedUpdatedMixin):
    cohort = models.ForeignKey(
        LiveCohort, on_delete=models.CASCADE, related_name='cohort_quizzes'
    )
    quiz = models.ForeignKey('quizzes.Quiz', on_delete=models.CASCADE)

    due_date = models.DateTimeField()  
    is_required = models.BooleanField(default=True)
    points = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['cohort', 'quiz']
