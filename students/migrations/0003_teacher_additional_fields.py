# Generated migration for teacher additional fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_student_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='specialization',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='experience',
            field=models.IntegerField(default=0, help_text='Years of experience'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='profile_picture',
            field=models.ImageField(upload_to='teacher_profiles/', blank=True, null=True),
        ),
    ]
