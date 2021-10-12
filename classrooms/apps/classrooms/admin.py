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
    """Admin configuration for the Classroom model."""

    list_display = [
        "uuid",
        "name",
        "active",
        "school",
    ]
    list_filter = ["active"]


@admin.register(ClassroomEnrollment)
class ClassroomEnrollmentAdmin(admin.ModelAdmin):
    """Admin configuration for the ClassroomEnrollment model."""

    list_display = [
        "user_id",
        "classroom_instance",
        "staff",
    ]
    list_filter = ["staff"]
    search_fields = ["user_id"]


@admin.register(CourseAssignment)
class CourseAssignmentAdmin(admin.ModelAdmin):
    """Admin configuration for the CourseAssignment model."""

    list_display = [
        "course_id",
        "classroom_instance",
    ]
    search_fields = ["course_id"]


@admin.register(ClassroomFeatureRole)
class ClassroomFeatureRoleAdmin(admin.ModelAdmin):
    pass


@admin.register(ClassroomRoleAssignment)
class ClassroomRoleAssignmentAdmin(admin.ModelAdmin):
    pass
