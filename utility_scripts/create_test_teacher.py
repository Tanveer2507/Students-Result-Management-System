import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'srms_project.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from students.models import Teacher, Subject

def create_test_teacher():
    """Create a test teacher"""
    
    print("="*60)
    print("CREATING TEST TEACHER...")
    print("="*60)
    
    # Check if teacher already exists
    if User.objects.filter(username='testteacher').exists():
        print("\n⚠️  Test teacher already exists!")
        print("Login with: testteacher / test123")
        return
    
    try:
        # Create User
        user = User.objects.create_user(
            username='testteacher',
            password='test123',
            first_name='John',
            last_name='Teacher',
            email='teacher@test.com'
        )
        print(f"✅ Created User: {user.username}")
        
        # Create UserProfile
        user_profile = UserProfile.objects.create(
            user=user,
            role='teacher',
            phone='9876543210',
            address='456 Teacher Street, Education City'
        )
        print(f"✅ Created UserProfile")
        
        # Create Teacher profile
        teacher = Teacher.objects.create(
            user=user,
            employee_id='TCH001',
            phone='9876543210',
            qualification='M.Sc, B.Ed',
            specialization='Mathematics & Science',
            experience=5,
            address='456 Teacher Street, Education City'
        )
        print(f"✅ Created Teacher profile")
        
        # Assign subjects if they exist
        subjects = Subject.objects.all()[:3]  # Assign first 3 subjects
        if subjects:
            teacher.subjects.set(subjects)
            print(f"✅ Assigned {subjects.count()} subjects")
        
        print("\n" + "="*60)
        print("🎉 TEST TEACHER CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"\n📋 Login Credentials:")
        print(f"   Username: testteacher")
        print(f"   Password: test123")
        print(f"\n🔗 Login URL:")
        print(f"   http://127.0.0.1:8000/accounts/login/teacher/")
        print(f"\n👤 Teacher Details:")
        print(f"   Name: {user.get_full_name()}")
        print(f"   Employee ID: {teacher.employee_id}")
        print(f"   Qualification: {teacher.qualification}")
        print(f"   Specialization: {teacher.specialization}")
        print(f"   Experience: {teacher.experience} years")
        print(f"   Subjects: {subjects.count()}")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == '__main__':
    create_test_teacher()
