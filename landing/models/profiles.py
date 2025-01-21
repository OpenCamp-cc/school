from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models, transaction

from db.models import BaseModel, CreatedUpdatedMixin


class Orderable(models.Model):
    """
    Abstract model that handles ordering functionality.
    Models using this must define get_ordering_queryset() method to specify
    which objects to compare when calculating the next order value.
    """

    order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ['order']

    def get_ordering_queryset(self):
        raise ImproperlyConfigured(
            f'{self.__class__.__name__} must implement get_ordering_queryset() method'
        )

    def save(self, *args, **kwargs):
        """Save the model instance and reorder items if necessary"""

        with transaction.atomic():
            if self._state.adding:
                if not self.order:
                    last_item = self.get_ordering_queryset().order_by('-order').first()
                    self.order = (last_item.order + 1) if last_item else 0
            else:
                old_obj = self.__class__.objects.get(pk=self.pk)
                if old_obj.order != self.order:
                    self.get_ordering_queryset().filter(pk=self.pk).update(order=99999)

                    if self.order > old_obj.order:
                        self.get_ordering_queryset().filter(
                            order__gt=old_obj.order, order__lte=self.order
                        ).exclude(pk=self.pk).update(order=models.F('order') - 1)
                    else:
                        self.get_ordering_queryset().filter(
                            order__gte=self.order, order__lt=old_obj.order
                        ).exclude(pk=self.pk).update(order=models.F('order') + 1)

            super().save(*args, **kwargs)


class Profile(BaseModel, CreatedUpdatedMixin):
    """
    The profile model holds information about the user that will be displayed on
    their "landing" page a.k.a the Linktree page.
    Contains basic user info, social media links, and can have multiple links
    organized in optional categories through ProfileCategory and ProfileLink models.
    """

    user = models.OneToOneField(
        'users.User', on_delete=models.CASCADE, related_name='landing_profile'
    )
    name = models.CharField(max_length=32)
    bio = models.CharField(max_length=128, null=True, blank=True)
    profile_image = models.ImageField(
        upload_to='landing/profiles/', null=True, blank=True
    )
    background_image = models.ImageField(
        upload_to='landing/backgrounds/', null=True, blank=True
    )

    threads_url = models.URLField(null=True, blank=True, max_length=512)
    instagram_url = models.URLField(null=True, blank=True, max_length=512)
    email_url = models.EmailField(null=True, blank=True, max_length=512)
    facebook_url = models.URLField(null=True, blank=True, max_length=512)
    youtube_url = models.URLField(null=True, blank=True, max_length=512)
    twitter_url = models.URLField(null=True, blank=True, max_length=512)
    website_url = models.URLField(null=True, blank=True, max_length=512)

    def __str__(self):
        return self.name


class ProfileCategory(BaseModel, CreatedUpdatedMixin, Orderable):
    """
    The ProfileCategory model is used to group links together. Each category
    can have its own name.
    The user can order the categories which is stored in the `order` field.
    Users can hide or delete an entire category without removing the data.
    """

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=64, null=True, blank=True)
    is_hidden = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta(Orderable.Meta):
        unique_together = ['profile', 'order']

    def get_ordering_queryset(self):
        return ProfileCategory.objects.filter(profile=self.profile)

    def __str__(self):
        return self.title


class ProfileLink(BaseModel, CreatedUpdatedMixin, Orderable):
    """
    The ProfileLink model represents a link on the user's landing page.
    Each link has a title, thumbnail, URL, and an optional category it belongs to.
    Links can be ordered within their category or displayed at the bottom if uncategorized.
    Links can be hidden or deleted without removing the data.
    """

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    profile_category = models.ForeignKey(
        ProfileCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='categorized_links',
    )
    title = models.CharField(max_length=64, null=True, blank=True)
    thumbnail = models.ImageField(upload_to='landing/links/', null=True, blank=True)
    url = models.URLField(null=True, max_length=512)
    is_hidden = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    click_count = models.PositiveIntegerField(default=0)

    class Meta(Orderable.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['profile_category', 'order'],
                condition=models.Q(profile_category__isnull=False),
                name='unique_category_order',
            ),
            models.UniqueConstraint(
                fields=['profile', 'order'],
                condition=models.Q(profile_category__isnull=True),
                name='unique_profile_order_for_uncategorized',
            ),
        ]

    def get_ordering_queryset(self):
        if self.profile_category:
            return ProfileLink.objects.filter(profile_category=self.profile_category)
        return ProfileLink.objects.filter(
            profile=self.profile, profile_category__isnull=True
        )

    def clean(self):
        if self.profile_category and self.profile != self.profile_category.profile:
            raise ValidationError(
                {'profile': "Link's profile must match the profile of its category"}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
