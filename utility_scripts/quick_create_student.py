import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'srms_project.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from students.models import Student, Class
from datetime import date
import random

def quick_create_student():
    """Quickly create a student with auto-generated data"""
    
    # Generate unique username and roll number
    random_num = random.randint(1000, 9999)
    username = f"student{random_num}"
    roll_number = f"2024{random_num}"
    
    # Check if username exists
    while User.objects.filter(username=username).exists():
        random_num = random.randint(1000, 9999)
        username = f"student{random_num}"
        roll_number = f"2024{random_num}"
    
    # Default password
    password = "student123"
    
    # Sample names
    first_names = ["John", "Emma", "Michael", "Sophia", "William", "Olivia", "James", "Ava", "Robert", "Isabella"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    email = f"{first_name.lower()}.{last_name.lower()}@example.com"
    
    # Get or create class
    student_class, created = Class.objects.get_or_create(
        name='Class 10',
        section='A'
    )
    
    # Random date of birth (age 15-17)
    year = random.randint(2007, 2009)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    dob = date(year, month, day)
    
    # Random gender
    gender = random.choice(['M', 'F'])
    
    # Family details
    father_name = f"{random.choice(['Mr. John', 'Mr. David', 'Mr. Michael', 'Mr. Robert'])} {last_name}"
    mother_name = f"{random.choice(['Mrs. Mary', 'Mrs. Sarah', 'Mrs. Emily', 'Mrs. Lisa'])} {last_name}"
    
    # Contact details
    phone = f"98765{random.randint(10000, 99999)}"
    address = f"{random.randint(1, 999)} Main Street, City - {random.randint(10000, 99999)}"
    
    print("="*60)
    print("QUICK CREATE STUDENT")
    print("="*60)
    
    try:
        # Create User
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        print(f"✅ Created User: {user.username}")
        
        # Create UserProfile
        user_profile = UserProfile.objects.create(
            user=user,
            role='student'
        )
        print(f"✅ Created UserProfile with role: {user_profile.role}")
        
        # Create Student profile
        student = Student.objects.create(
            user=user,
            roll_number=roll_number,
            student_class=student_class,
            date_of_birth=dob,
            gender=gender,
            father_name=father_name,
            mother_name=mother_name,
            phone=phone,
            address=address
        )
        print(f"✅ Created Student profile: {student.roll_number}")
        
        print("\n" + "="*60)
        print("🎉 STUDENT CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"\n📋 Login Credentials:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"\n🔗 Login URL:")
        print(f"   http://127.0.0.1:8000/accounts/login/student/")
        print(f"\n👤 Student Details:")
        print(f"   Name: {user.get_full_name()}")
        print(f"   Roll Number: {student.roll_number}")
        print(f"   Class: {student.student_class}")
        print(f"   Email: {user.email}")
        print(f"   Phone: {student.phone}")
        print(f"   Gender: {student.get_gender_display()}")
        print("\n" + "="*60)
        print("✨ Login and start using the system!")
        print("="*60)
        
        return {
            'username': username,
            'password': password,
            'name': user.get_full_name(),
            'roll_number': roll_number
        }
        
    except Exception as e:
        print(f"\n❌ Error creating student: {str(e)}")
        return None

if __name__ == '__main__':
    quick_create_student()
