import os
import uuid

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import IntegrityError, models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from db.models import BaseModel, CreatedUpdatedMixin
from integrations.emails import plunk_client


class User(AbstractUser, CreatedUpdatedMixin):
    id = models.AutoField(primary_key=True)
    objects: UserManager = UserManager()

    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='users/', null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)

    email = models.EmailField(unique=True)

    def __str__(self):
        return f'{self.name}: {self.email}'

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'


class ExternalProfile(CreatedUpdatedMixin, BaseModel):
    google_access_token = models.CharField(max_length=100, blank=True, null=True)
    google_refresh_token = models.CharField(max_length=100, blank=True, null=True)
    google_token_uri = models.CharField(max_length=255, blank=True, null=True)
    google_scopes = models.CharField(max_length=255, blank=True, null=True)
    google_enabled = models.BooleanField(default=False)

    user = models.OneToOneField(
        'users.User', on_delete=models.CASCADE, related_name='external_profile'
    )


class SignupInviteManager(models.Manager):
    def create_invite(
        self,
        invited_by: User,
        user: User,
    ) -> 'SignupInvite':
        code = str(uuid.uuid4()).replace('-', '')
        return self.create(invited_by=invited_by, user=user, code=code)


class SignupInvite(CreatedUpdatedMixin, BaseModel):
    objects: SignupInviteManager = SignupInviteManager()
    invited_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='invited_users'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='signup_invites'
    )
    code = models.CharField(max_length=255, unique=True)
    invited = models.BooleanField(default=False)


@receiver(post_save, sender=User)
def create_external_profile(sender, instance, created, **kwargs):
    if created:
        try:
            ExternalProfile.objects.create(user=instance)
        except IntegrityError:
            pass
