"""
Create a test student account for testing the student portal
Usage: python manage.py shell < create_test_student.py
"""

import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'srms_project.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from students.models import Student, Class, Subject
from results.models import Marks, Result

print("Creating test student account...")

# Create or get class
class_obj, _ = Class.objects.get_or_create(name="10th", section="A")
print(f"✓ Class: {class_obj}")

# Create subjects if they don't exist
subjects_data = [
    {"name": "Mathematics", "code": "MATH101"},
    {"name": "Science", "code": "SCI101"},
    {"name": "English", "code": "ENG101"},
]

subjects = []
for subj_data in subjects_data:
    subject, _ = Subject.objects.get_or_create(
        code=subj_data["code"],
        defaults={
            "name": subj_data["name"],
            "class_assigned": class_obj,
            "max_marks": 100,
            "pass_marks": 35
        }
    )
    subjects.append(subject)
    print(f"✓ Subject: {subject.name}")

# Create test student user
if not User.objects.filter(username="student1").exists():
    user = User.objects.create_user(
        username="student1",
        email="student1@example.com",
        password="student123",
        first_name="John",
        last_name="Doe"
    )
    print(f"✓ User created: {user.username}")
    
    # Create user profile
    UserProfile.objects.create(
        user=user,
        role="student",
        phone="1234567890"
    )
    print("✓ User profile created")
    
    # Create student record
    student = Student.objects.create(
        user=user,
        roll_number="2024001",
        student_class=class_obj,
        date_of_birth=date(2008, 1, 15),
        gender="M",
        father_name="Robert Doe",
        mother_name="Mary Doe",
        phone="1234567890",
        address="123 Main Street, City"
    )
    print(f"✓ Student created: {student.roll_number}")
    
    # Add sample marks
    marks_data = [
        {"subject": subjects[0], "marks": 85},  # Math
        {"subject": subjects[1], "marks": 78},  # Science
        {"subject": subjects[2], "marks": 92},  # English
    ]
    
    for mark_data in marks_data:
        Marks.objects.create(
            student=student,
            subject=mark_data["subject"],
            marks_obtained=mark_data["marks"],
            exam_date=date.today()
        )
        print(f"✓ Marks added: {mark_data['subject'].name} - {mark_data['marks']}")
    
    # Calculate and create result
    total_marks = sum(m["marks"] for m in marks_data)
    total_max = sum(s.max_marks for s in subjects)
    percentage = (total_marks / total_max) * 100
    
    Result.objects.create(
        student=student,
        total_marks=total_marks,
        percentage=percentage,
        published=True
    )
    print(f"✓ Result generated: {percentage:.2f}%")
    
    print("\n" + "="*50)
    print("✅ Test student created successfully!")
    print("="*50)
    print("\nLogin Credentials:")
    print(f"  Username: student1")
    print(f"  Password: student123")
    print(f"\nStudent Details:")
    print(f"  Name: John Doe")
    print(f"  Roll Number: 2024001")
    print(f"  Class: 10th - A")
    print(f"  Total Marks: {total_marks}/300")
    print(f"  Percentage: {percentage:.2f}%")
    print("\nTest the student portal:")
    print("  1. Go to http://127.0.0.1:8000/")
    print("  2. Login with student1 / student123")
    print("  3. Explore all features!")
    print("="*50)
else:
    print("⚠️  Test student already exists!")
    print("   Username: student1")
    print("   Password: student123")
