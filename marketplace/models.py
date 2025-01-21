from django.db import models

from db.models import BaseModel, CreatedUpdatedMixin
from languages.models import Language
from users.models import User


class TeacherProfile(CreatedUpdatedMixin, BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    profile_picture = models.ImageField(
        upload_to='teacher_profiles', null=True, blank=True
    )
    rating = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)
    rating_sum = models.IntegerField(default=0)

    title = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255)
    is_certified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class TeacherCertificate(CreatedUpdatedMixin, BaseModel):
    teacher_profile = models.ForeignKey(
        'TeacherProfile', on_delete=models.CASCADE, related_name='certificates'
    )
    certificate_name = models.CharField(max_length=255)
    year_of_issue = models.IntegerField()
    certificate = models.ImageField(upload_to='teacher_certificates')

    def __str__(self):
        return f'{self.teacher_profile.user.first_name} {self.teacher_profile.user.last_name}'


class TeacherLanguageProficiency(CreatedUpdatedMixin, BaseModel):
    teacher_profile = models.ForeignKey(
        'TeacherProfile',
        on_delete=models.CASCADE,
        related_name='language_proficiencies',
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    proficiency = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.teacher_profile.user.first_name} {self.teacher_profile.user.last_name}'


class StudentProfile(CreatedUpdatedMixin, BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    profile_picture = models.ImageField(
        upload_to='student_profiles', null=True, blank=True
    )
    rating = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)
    rating_sum = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
