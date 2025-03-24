from django.contrib import admin

from .models import (
    LiveCohort,
    LiveCohortAssignment,
    LiveCohortAssignmentSubmission,
    LiveCohortQuiz,
    LiveCohortRegistration,
    LiveCohortSession,
    LiveCohortWaitList,
)


@admin.register(LiveCohort)
class LiveCohortAdmin(admin.ModelAdmin):
    pass


@admin.register(LiveCohortSession)
class LiveCohortSessionAdmin(admin.ModelAdmin):
    pass


@admin.register(LiveCohortAssignmentSubmission)
class LiveCohortAssignmentSubmissionAdmin(admin.ModelAdmin):
    pass


@admin.register(LiveCohortRegistration)
class LiveCohortRegistrationAdmin(admin.ModelAdmin):
    pass


@admin.register(LiveCohortAssignment)
class LiveCohortAssignmentAdmin(admin.ModelAdmin):
    pass


@admin.register(LiveCohortQuiz)
class LiveCohortQuizAdmin(admin.ModelAdmin):
    pass


@admin.register(LiveCohortWaitList)
class LiveCohortWaitListAdmin(admin.ModelAdmin):
    pass