"""
Admin configuration for classroom models.
"""
from django.contrib import admin

from classrooms.apps.classrooms.models import (
    Classroom,
    ClassroomEnrollement,
    ClassroomRoleAssignment,
    ClassroomFeatureRole,
)


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    pass


@admin.register(ClassroomEnrollement)
class ClassroomEnrollmentAdmin(admin.ModelAdmin):
    pass


@admin.register(ClassroomFeatureRole)
class ClassroomFeatureRoleAdmin(admin.ModelAdmin):
    pass


@admin.register(ClassroomRoleAssignment)
class ClassroomRoleAssignmentAdmin(admin.ModelAdmin):
    pass
