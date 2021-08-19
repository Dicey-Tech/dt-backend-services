# Generated by Django 2.2.24 on 2021-08-19 14:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('school', models.UUIDField(help_text='School uuid.')),
                ('name', models.CharField(default='Your Classroom Name', help_text='Specifies the displayed name of the classroom', max_length=255)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Classroom',
                'verbose_name_plural': 'Classrooms',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='ClassroomFeatureRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(db_index=True, max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClassroomRoleAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('applies_to_all_contexts', models.BooleanField(default=False, help_text='If true, indicates that the user is effectively assigned their role for any and all contexts. Defaults to False.')),
                ('enterprise_customer_uuid', models.UUIDField(blank=True, null=True, verbose_name='Enterprise Customer UUID')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classroom.ClassroomFeatureRole')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClassroomEnrollement',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user_id', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('classroom_instance', models.ForeignKey(blank=True, help_text='The classroom to which this enrollment is attached', null=True, on_delete=django.db.models.deletion.CASCADE, to='classroom.Classroom')),
            ],
            options={
                'ordering': ['created'],
                'unique_together': {('classroom_instance', 'user_id')},
            },
        ),
    ]
