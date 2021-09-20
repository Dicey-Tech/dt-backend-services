"""
Admin configuration for classroom models.
"""
from django.contrib import admin

from classrooms.apps.classrooms.models import (
    Classroom,
    ClassroomEnrollment,
    CourseAssignment,
    ClassroomRoleAssignment,
    ClassroomFeatureRole,
)


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    pass


@admin.register(ClassroomEnrollment)
class ClassroomEnrollmentAdmin(admin.ModelAdmin):
    pass


@admin.register(CourseAssignment)
class CourseAssignmentAdmin(admin.ModelAdmin):
    pass


@admin.register(ClassroomFeatureRole)
class ClassroomFeatureRoleAdmin(admin.ModelAdmin):
    pass


@admin.register(ClassroomRoleAssignment)
class ClassroomRoleAssignmentAdmin(admin.ModelAdmin):
    pass
