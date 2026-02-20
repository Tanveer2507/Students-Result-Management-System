# Generated migration for adding unique constraints and teacher email

from django.db import migrations, models


def add_default_emails(apps, schema_editor):
    """Add default emails to existing teachers"""
    Teacher = apps.get_model('students', 'Teacher')
    for teacher in Teacher.objects.all():
        # Create unique email from employee_id
        teacher.email = f"{teacher.employee_id.lower()}@school.com"
        teacher.save()


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_teacher_additional_fields'),
    ]

    operations = [
        # Add email field to Teacher (nullable first)
        migrations.AddField(
            model_name='teacher',
            name='email',
            field=models.EmailField(null=True, blank=True),
        ),
        # Populate emails for existing teachers
        migrations.RunPython(add_default_emails, migrations.RunPython.noop),
        # Make email unique and non-nullable
        migrations.AlterField(
            model_name='teacher',
            name='email',
            field=models.EmailField(unique=True),
        ),
        # Add unique constraint to Student phone
        migrations.AlterField(
            model_name='student',
            name='phone',
            field=models.CharField(max_length=15, unique=True),
        ),
        # Add unique constraint to Teacher phone
        migrations.AlterField(
            model_name='teacher',
            name='phone',
            field=models.CharField(max_length=15, unique=True),
        ),
    ]
