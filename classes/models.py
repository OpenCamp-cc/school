from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from db.models import BaseModel, CreatedUpdatedMixin
from users.models import User


class LiveCohort(BaseModel, CreatedUpdatedMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    max_students = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(99), MinValueValidator(1)]
    )

    # price for the class, in USD only for now
    price = models.DecimalField(max_digits=6, decimal_places=2)

    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cohorts_taught'
    )
    students = models.ManyToManyField(User, through='LiveCohortRegistration')
    sessions: models.QuerySet['LiveCohortSession']

    def __str__(self):
        return self.name


class LiveCohortSession(BaseModel, CreatedUpdatedMixin):
    cohort = models.ForeignKey(
        LiveCohort, on_delete=models.CASCADE, related_name='sessions'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

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
