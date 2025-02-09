import os
from datetime import datetime, timedelta
from typing import List

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import IntegrityError, models
from django.urls import reverse
from django.utils import timezone

from db.models import BaseModel, CreatedUpdatedMixin
from integrations.emails import plunk_client
from users.models import SignupInvite, User


class LiveCohort(BaseModel, CreatedUpdatedMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    features = models.TextField(blank=True, null=True)
    key_topics = models.TextField(blank=True, null=True)
    schedule = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    course_fees = models.TextField(blank=True, null=True)

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

    upcoming_assignments: List['LiveCohortAssignment']
    upcoming_sessions: List['LiveCohortSession']
    has_more_sessions: bool
    has_more_assignments: bool
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


class LiveCohortRegistrationManager(models.Manager):
    def register_student(
        self, cohort: LiveCohort, student: User
    ) -> 'LiveCohortRegistration':
        if cohort.students.count() >= cohort.max_students:
            raise Exception('Cohort is full')

        return self.create(cohort=cohort, student=student)

    def register_new_student(
        self, cohort: LiveCohort, first_name: str, last_name: str, email: str
    ) -> 'LiveCohortRegistration':
        if cohort.students.count() >= cohort.max_students:
            raise Exception('Cohort is full')

        try:
            student = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=email,
                email=email,
                is_active=False,
            )
        except IntegrityError:
            pass

        registration = self.create(cohort=cohort, student=student)
        invite = SignupInvite.objects.create_invite(
            invited_by=cohort.teacher, user=student
        )

        server_host = os.getenv('SERVER_HOST', '')
        signup_url = reverse('users:signup')
        message = f"<p>Hi {student.first_name},</p><p>Your registration for {cohort.name} has been confirmed.</p><p>Click here to join open camp's learning platform: {server_host}{signup_url}?code={invite.code}</p><br/><p>Thanks,<br/>Victor</p>"

        plunk_client.send_email(
            [student.email],
            f'open camp: registration for {cohort.name} confirmed',
            message,
        )

        return registration


class LiveCohortRegistration(BaseModel):
    objects: LiveCohortRegistrationManager = LiveCohortRegistrationManager()
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
    submission_optional = models.BooleanField(default=False)
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
