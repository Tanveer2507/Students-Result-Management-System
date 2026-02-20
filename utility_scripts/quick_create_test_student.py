import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'srms_project.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from students.models import Student, Class
from datetime import date

def create_test_student():
    """Quickly create a test student"""
    
    print("="*60)
    print("CREATING TEST STUDENT...")
    print("="*60)
    
    # Check if student already exists
    if User.objects.filter(username='teststudent').exists():
        print("\n⚠️  Test student already exists!")
        print("Login with: teststudent / test123")
        return
    
    try:
        # Get or create a class
        student_class, created = Class.objects.get_or_create(
            name="Class 10",
            section="A"
        )
        
        # Create User
        user = User.objects.create_user(
            username='teststudent',
            password='test123',
            first_name='Test',
            last_name='Student',
            email='test@student.com'
        )
        print(f"✅ Created User: {user.username}")
        
        # Create UserProfile
        user_profile = UserProfile.objects.create(
            user=user,
            role='student'
        )
        print(f"✅ Created UserProfile")
        
        # Create Student profile
        student = Student.objects.create(
            user=user,
            roll_number='TS001',
            student_class=student_class,
            date_of_birth=date(2008, 5, 15),
            gender='M',
            father_name='Test Father',
            mother_name='Test Mother',
            phone='1234567890',
            address='123 Test Street, Test City'
        )
        print(f"✅ Created Student profile")
        
        print("\n" + "="*60)
        print("🎉 TEST STUDENT CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"\n📋 Login Credentials:")
        print(f"   Username: teststudent")
        print(f"   Password: test123")
        print(f"\n🔗 Login URL:")
        print(f"   http://127.0.0.1:8000/accounts/login/student/")
        print(f"\n👤 Student Details:")
        print(f"   Name: {user.get_full_name()}")
        print(f"   Roll Number: {student.roll_number}")
        print(f"   Class: {student.student_class}")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == '__main__':
    create_test_student()
