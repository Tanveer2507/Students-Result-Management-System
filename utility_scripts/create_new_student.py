import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'srms_project.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from students.models import Student, Class
from results.models import Marks, Result
from datetime import date

def create_new_student():
    """Create a new student profile"""
    
    print("="*60)
    print("CREATE NEW STUDENT PROFILE")
    print("="*60)
    
    # Get student details
    username = input("\nEnter username: ").strip()
    
    # Check if username already exists
    if User.objects.filter(username=username).exists():
        print(f"\n❌ Error: Username '{username}' already exists!")
        print("Please try again with a different username.")
        return
    
    password = input("Enter password: ").strip()
    first_name = input("Enter first name: ").strip()
    last_name = input("Enter last name: ").strip()
    email = input("Enter email: ").strip()
    
    # Student specific details
    roll_number = input("Enter roll number: ").strip()
    
    # Check if roll number already exists
    if Student.objects.filter(roll_number=roll_number).exists():
        print(f"\n❌ Error: Roll number '{roll_number}' already exists!")
        print("Please try again with a different roll number.")
        return
    
    # Show available classes
    print("\nAvailable Classes:")
    classes = Class.objects.all()
    for i, cls in enumerate(classes, 1):
        print(f"{i}. {cls}")
    
    if not classes:
        print("No classes available. Creating default class...")
        student_class = Class.objects.create(name="Class 10", section="A")
    else:
        class_choice = input(f"\nSelect class (1-{classes.count()}): ").strip()
        try:
            student_class = classes[int(class_choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice. Using first class.")
            student_class = classes.first()
    
    # Date of birth
    print("\nEnter Date of Birth:")
    year = input("Year (e.g., 2008): ").strip()
    month = input("Month (1-12): ").strip()
    day = input("Day (1-31): ").strip()
    
    try:
        dob = date(int(year), int(month), int(day))
    except ValueError:
        print("Invalid date. Using default: 2008-01-01")
        dob = date(2008, 1, 1)
    
    # Gender
    print("\nSelect Gender:")
    print("1. Male")
    print("2. Female")
    print("3. Other")
    gender_choice = input("Choice (1-3): ").strip()
    gender_map = {'1': 'M', '2': 'F', '3': 'O'}
    gender = gender_map.get(gender_choice, 'M')
    
    # Family details
    father_name = input("\nEnter father's name: ").strip()
    mother_name = input("Enter mother's name: ").strip()
    
    # Contact details
    phone = input("Enter phone number: ").strip()
    address = input("Enter address: ").strip()
    
    print("\n" + "="*60)
    print("CREATING STUDENT PROFILE...")
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
        print("🎉 STUDENT PROFILE CREATED SUCCESSFULLY!")
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
        print(f"   Date of Birth: {student.date_of_birth}")
        print(f"   Gender: {student.get_gender_display()}")
        print(f"   Father's Name: {student.father_name}")
        print(f"   Mother's Name: {student.mother_name}")
        print(f"   Address: {student.address}")
        print("\n" + "="*60)
        print("✨ You can now login with these credentials!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error creating student: {str(e)}")
        print("Please try again.")

if __name__ == '__main__':
    create_new_student()
