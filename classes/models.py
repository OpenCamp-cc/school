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


class PrivatePackage(BaseModel, CreatedUpdatedMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='private_packages'
    )
    price = models.DecimalField(max_digits=6, decimal_places=2)
    original_price = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    num_sessions = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(15)]
    )

    def __str__(self):
        return f'{self.name} - {self.teacher}'


class SelfPacedClass(BaseModel, CreatedUpdatedMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # price for the class, in USD only for now
    price = models.DecimalField(max_digits=6, decimal_places=2)

    # optional start and end date for the class to be completed
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='self_paced_classes_taught'
    )
    students = models.ManyToManyField(User, through='SelfPacedClassRegistration')

    def __str__(self):
        return self.name


class SelfPacedClassRegistration(BaseModel):
    sp_class = models.ForeignKey(SelfPacedClass, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    registration_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student} - {self.sp_class}'


class SelfPacedLesson(BaseModel, CreatedUpdatedMixin):
    sp_class = models.ForeignKey(
        SelfPacedClass, on_delete=models.CASCADE, related_name='lessons'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    lesson_number = models.PositiveSmallIntegerField(default=1)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.sp_class} - {self.lesson_number} - {self.name}'


class SelfPacedLessonHomework(BaseModel, CreatedUpdatedMixin):
    lesson = models.ForeignKey(
        SelfPacedLesson, on_delete=models.CASCADE, related_name='homework'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.lesson} - {self.name}'


class SelfPacedClassUpload(BaseModel, CreatedUpdatedMixin):
    sp_class = models.ForeignKey(
        SelfPacedClass, on_delete=models.CASCADE, related_name='uploads'
    )
    lesson = models.ForeignKey(
        SelfPacedLesson,
        on_delete=models.CASCADE,
        related_name='uploads',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='self_paced/uploads')

    def __str__(self):
        return f'{self.sp_class} - {self.name}'
