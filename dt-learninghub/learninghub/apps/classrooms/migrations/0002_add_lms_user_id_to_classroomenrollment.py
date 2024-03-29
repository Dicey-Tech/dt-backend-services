# Generated by Django 3.2.12 on 2022-03-30 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("classrooms", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="classroomenrollment",
            name="lms_user_id",
            field=models.PositiveIntegerField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name="classroomenrollment",
            name="user_id",
            field=models.EmailField(help_text="User identifier", max_length=254),
        ),
    ]
