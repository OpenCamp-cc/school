from django.contrib import admin

from .models import (
    LiveCohort,
    LiveCohortAssignment,
    LiveCohortRegistration,
    LiveCohortSession,
)


@admin.register(LiveCohort)
class LiveCohortAdmin(admin.ModelAdmin):
    pass


@admin.register(LiveCohortSession)
class LiveCohortSessionAdmin(admin.ModelAdmin):
    pass


@admin.register(LiveCohortRegistration)
class LiveCohortRegistrationAdmin(admin.ModelAdmin):
    pass


@admin.register(LiveCohortAssignment)
class LiveCohortAssignmentAdmin(admin.ModelAdmin):
    pass
