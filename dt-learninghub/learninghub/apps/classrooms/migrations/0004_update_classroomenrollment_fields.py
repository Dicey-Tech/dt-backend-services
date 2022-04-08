# Generated by Django 3.2.12 on 2022-03-31 10:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("classrooms", "0003_backfill_lms_user_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="classroomenrollment",
            old_name="user_id",
            new_name="user_email",
        ),
        migrations.AlterUniqueTogether(
            name="classroomenrollment",
            unique_together={("classroom_instance", "lms_user_id")},
        ),
    ]