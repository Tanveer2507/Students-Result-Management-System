import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'srms_project.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from students.models import Student, Class
from datetime import date

def create_student_profile():
    """Create a complete test student profile"""
    
    # Check if student already exists
    if User.objects.filter(username='student_demo').exists():
        print("Student 'student_demo' already exists!")
        user = User.objects.get(username='student_demo')
        print(f"Username: student_demo")
        print(f"Password: demo123")
        print(f"Login at: http://127.0.0.1:8000/accounts/login/student/")
        return
    
    # Create User
    user = User.objects.create_user(
        username='student_demo',
        password='demo123',
        first_name='Sarah',
        last_name='Johnson',
        email='sarah.johnson@example.com'
    )
    print(f"✅ Created User: {user.username}")
    
    # Create UserProfile
    user_profile = UserProfile.objects.create(
        user=user,
        role='student'
    )
    print(f"✅ Created UserProfile with role: {user_profile.role}")
    
    # Get or create a class
    student_class, created = Class.objects.get_or_create(
        name='Class 10',
        section='A'
    )
    if created:
        print(f"✅ Created Class: {student_class}")
    else:
        print(f"✅ Using existing Class: {student_class}")
    
    # Create Student profile
    student = Student.objects.create(
        user=user,
        roll_number='2024100',
        student_class=student_class,
        date_of_birth=date(2008, 5, 15),
        gender='Female',
        phone='9876543210',
        address='123 Main Street, Downtown, City - 12345',
        father_name='Robert Johnson',
        mother_name='Emily Johnson'
    )
    print(f"✅ Created Student profile: {student.roll_number}")
    
    print("\n" + "="*60)
    print("🎉 STUDENT PROFILE CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📋 Login Credentials:")
    print(f"   Username: student_demo")
    print(f"   Password: demo123")
    print(f"\n🔗 Login URL:")
    print(f"   http://127.0.0.1:8000/accounts/login/student/")
    print(f"\n👤 Student Details:")
    print(f"   Name: {user.get_full_name()}")
    print(f"   Roll Number: {student.roll_number}")
    print(f"   Class: {student.student_class}")
    print(f"   Email: {user.email}")
    print(f"   Phone: {student.phone}")
    print(f"   Date of Birth: {student.date_of_birth}")
    print(f"   Gender: {student.gender}")
    print(f"   Father's Name: {student.father_name}")
    print(f"   Mother's Name: {student.mother_name}")
    print(f"   Address: {student.address}")
    print("\n" + "="*60)
    print("✨ You can now login and access the student portal!")
    print("="*60)

if __name__ == '__main__':
    create_student_profile()
