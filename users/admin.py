from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DJUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdmin(DJUserAdmin):
    list_display = (
        'email',
        'first_name',
        'is_staff',
        'is_superuser',
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets += (
            (
                'Custom fields',
                {
                    'fields': (
                        'bio',
                        'profile_image',
                        'location',
                    ),
                },
            ),
        )
        return fieldsets


admin.site.register(User, UserAdmin)
