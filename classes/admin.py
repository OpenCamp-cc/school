from django.contrib import admin

from .models import (
    LiveCohort,
    LiveCohortRegistration,
    LiveCohortSession,
    PrivatePackage,
    SelfPacedClass,
    SelfPacedClassRegistration,
)


@admin.register(LiveCohort)
class LiveCohortAdmin(admin.ModelAdmin):
    pass


@admin.register(LiveCohortSession)
class LiveCohortSessionAdmin(admin.ModelAdmin):
    pass


@admin.register(PrivatePackage)
class PrivatePackageAdmin(admin.ModelAdmin):
    pass


@admin.register(LiveCohortRegistration)
class LiveCohortRegistrationAdmin(admin.ModelAdmin):
    pass


@admin.register(SelfPacedClass)
class SelfPacedClassAdmin(admin.ModelAdmin):
    pass


@admin.register(SelfPacedClassRegistration)
class SelfPacedClassRegistrationAdmin(admin.ModelAdmin):
    pass
