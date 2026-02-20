import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'srms_project.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from students.models import Student
from results.models import Marks, Result

def verify_student():
    """Verify test student exists and has all data"""
    
    print("="*60)
    print("VERIFYING TEST STUDENT DATA")
    print("="*60)
    
    try:
        # Check User
        user = User.objects.get(username='teststudent')
        print(f"\n✅ User found: {user.username}")
        print(f"   - Full Name: {user.get_full_name()}")
        print(f"   - Email: {user.email}")
        print(f"   - Is Active: {user.is_active}")
        
        # Check UserProfile
        try:
            profile = UserProfile.objects.get(user=user)
            print(f"\n✅ UserProfile found")
            print(f"   - Role: {profile.role}")
        except UserProfile.DoesNotExist:
            print("\n❌ UserProfile NOT found!")
            return
        
        # Check Student
        try:
            student = Student.objects.get(user=user)
            print(f"\n✅ Student profile found")
            print(f"   - Roll Number: {student.roll_number}")
            print(f"   - Class: {student.student_class}")
            print(f"   - Phone: {student.phone}")
        except Student.DoesNotExist:
            print("\n❌ Student profile NOT found!")
            return
        
        # Check Marks
        marks = Marks.objects.filter(student=student)
        print(f"\n✅ Marks found: {marks.count()} subjects")
        for mark in marks:
            print(f"   - {mark.subject.name}: {mark.marks_obtained}/{mark.subject.max_marks}")
        
        # Check Result
        try:
            result = Result.objects.get(student=student)
            print(f"\n✅ Result found")
            print(f"   - Total Marks: {result.total_marks}")
            print(f"   - Percentage: {result.percentage}%")
            print(f"   - Grade: {result.grade}")
            print(f"   - Status: {result.status}")
            print(f"   - Published: {result.published}")
        except Result.DoesNotExist:
            print("\n❌ Result NOT found!")
        
        print("\n" + "="*60)
        print("✅ ALL DATA VERIFIED - STUDENT IS READY TO LOGIN")
        print("="*60)
        print(f"\n🔗 Login URL: http://127.0.0.1:8000/accounts/login/student/")
        print(f"📋 Username: teststudent")
        print(f"🔑 Password: test123")
        print("="*60)
        
    except User.DoesNotExist:
        print("\n❌ User 'teststudent' NOT found!")
        print("Please run: python quick_create_test_student.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == '__main__':
    verify_student()
