# Generated by Django 3.2.12 on 2022-03-30 13:31

from django.db import migrations
from learninghub.apps.api_client.lms import LMSApiClient


def backfill_lms_user_id(apps, schema_editor):

    lms_client = LMSApiClient()
    ClassroomEnrollment = apps.get_model("classrooms", "ClassroomEnrollment")

    for enrollment in ClassroomEnrollment.objects.filter(lms_user_id__isnull=True):
        enrollment.lms_user_id = lms_client.get_user_details(
            email=enrollment.user_id
        ).get("id")
        enrollment.save()


def remove_lms_user_id(apps, schema_editor):
    ClassroomEnrollment = apps.get_model("classrooms", "ClassroomEnrollment")

    for enrollment in ClassroomEnrollment.objects.filter(lms_user_id__isnull=True):
        enrollment.lms_user_id = None
        enrollment.save()


class Migration(migrations.Migration):

    dependencies = [
        ("classrooms", "0002_add_lms_user_id_to_classroomenrollment"),
    ]

    operations = [
        migrations.RunPython(backfill_lms_user_id, remove_lms_user_id),
    ]
