"""
Run this script to create sample data for testing
Usage: python manage.py shell < create_sample_data.py
"""

from django.contrib.auth.models import User
from accounts.models import UserProfile
from students.models import Class, Subject, Student, Teacher
from results.models import Marks, Result
from datetime import date

print("Creating sample data...")

# Create Classes
class_10a, _ = Class.objects.get_or_create(name="10th", section="A")
class_10b, _ = Class.objects.get_or_create(name="10th", section="B")
print("✓ Classes created")

# Create Subjects
subjects_data = [
    {"name": "Mathematics", "code": "MATH101", "class": class_10a},
    {"name": "Science", "code": "SCI101", "class": class_10a},
    {"name": "English", "code": "ENG101", "class": class_10a},
    {"name": "Social Studies", "code": "SS101", "class": class_10a},
]

for subj_data in subjects_data:
    Subject.objects.get_or_create(
        code=subj_data["code"],
        defaults={
            "name": subj_data["name"],
            "class_assigned": subj_data["class"],
            "max_marks": 100,
            "pass_marks": 35
        }
    )
print("✓ Subjects created")

# Create Teacher
if not User.objects.filter(username="teacher1").exists():
    teacher_user = User.objects.create_user(
        username="teacher1",
        email="teacher@srms.com",
        password="teacher123",
        first_name="Sarah",
        last_name="Smith"
    )
    UserProfile.objects.create(user=teacher_user, role="teacher", phone="9876543210")
    teacher = Teacher.objects.create(
        user=teacher_user,
        employee_id="EMP001",
        phone="9876543210",
        qualification="M.Sc Mathematics"
    )
    teacher.subjects.set(Subject.objects.filter(class_assigned=class_10a))
    print("✓ Teacher created (username: teacher1, password: teacher123)")

# Create Students
students_data = [
    {"username": "john_doe", "first": "John", "last": "Doe", "roll": "2024001"},
    {"username": "jane_smith", "first": "Jane", "last": "Smith", "roll": "2024002"},
    {"username": "mike_wilson", "first": "Mike", "last": "Wilson", "roll": "2024003"},
]

for std_data in students_data:
    if not User.objects.filter(username=std_data["username"]).exists():
        student_user = User.objects.create_user(
            username=std_data["username"],
            email=f"{std_data['username']}@example.com",
            password="student123",
            first_name=std_data["first"],
            last_name=std_data["last"]
        )
        UserProfile.objects.create(user=student_user, role="student")
        Student.objects.create(
            user=student_user,
            roll_number=std_data["roll"],
            student_class=class_10a,
            date_of_birth=date(2008, 1, 15),
            gender="M",
            father_name=f"Father of {std_data['first']}",
            mother_name=f"Mother of {std_data['first']}",
            phone="1234567890",
            address="123 Main Street"
        )

print("✓ Students created (username: john_doe, jane_smith, mike_wilson | password: student123)")

print("\n✅ Sample data created successfully!")
print("\nLogin Credentials:")
print("Admin: Use your superuser credentials")
print("Teacher: teacher1 / teacher123")
print("Student: john_doe / student123")
