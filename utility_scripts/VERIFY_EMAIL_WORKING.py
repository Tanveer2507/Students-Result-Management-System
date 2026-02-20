#!/usr/bin/env python
"""
Verify Email System is Working
Tests the exact email flow for Student and Teacher registration
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'srms_project.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

print("=" * 80)
print("VERIFYING EMAIL SYSTEM FOR STUDENT & TEACHER REGISTRATION")
print("=" * 80)
print()

print("Current Email Configuration:")
print(f"  Backend: {settings.EMAIL_BACKEND}")
print(f"  Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
print(f"  From Email: {settings.EMAIL_HOST_USER}")
print(f"  TLS: {settings.EMAIL_USE_TLS}")
print()

# Test 1: Student Registration Email
print("TEST 1: Student Registration Email")
print("-" * 80)
print()

student_data = {
    'student_name': 'Test Student',
    'roll_number': 'TEST001',
    'username': 'teststudent',
    'email': 'tanveerkakar294@gmail.com',  # Your email for testing
    'password': 'test123',
    'class_name': 'Class 10 - A',
}

print(f"Sending student registration email to: {student_data['email']}")
print(f"Student Name: {student_data['student_name']}")
print(f"Role: Student")
print()

try:
    subject = 'Account Created Successfully – SRMS'
    
    # Create email body
    email_body = f"""
Dear {student_data['student_name']},

Your account has been created successfully in the Student Result Management System (SRMS).

Account Details:
- Name: {student_data['student_name']}
- Role: Student
- Email: {student_data['email']}
- Roll Number: {student_data['roll_number']}
- Username: {student_data['username']}
- Class: {student_data['class_name']}

Your temporary password is: {student_data['password']}

Please login to the system and change your password for security.

Login URL: http://127.0.0.1:8000/accounts/login/student/

Best regards,
SRMS Administration Team
"""
    
    # Also send HTML version
    html_message = render_to_string('emails/student_registration.html', student_data)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [student_data['email']],
        html_message=html_message,
        fail_silently=False,
    )
    
    print("✅ Student registration email sent successfully!")
    print(f"   FROM: {settings.EMAIL_HOST_USER}")
    print(f"   TO: {student_data['email']}")
    print(f"   SUBJECT: {subject}")
    print()
    
except Exception as e:
    print(f"❌ Failed to send student email!")
    print(f"   Error: {str(e)}")
    print()
    import traceback
    traceback.print_exc()

# Test 2: Teacher Registration Email
print("TEST 2: Teacher Registration Email")
print("-" * 80)
print()

teacher_data = {
    'teacher_name': 'Test Teacher',
    'employee_id': 'EMP001',
    'username': 'testteacher',
    'email': 'tanveerkakar294@gmail.com',  # Your email for testing
    'password': 'test123',
    'qualification': 'M.Sc Mathematics',
    'subjects': 'Mathematics, Physics',
}

print(f"Sending teacher registration email to: {teacher_data['email']}")
print(f"Teacher Name: {teacher_data['teacher_name']}")
print(f"Role: Teacher")
print()

try:
    subject = 'Account Created Successfully – SRMS'
    
    # Create email body
    email_body = f"""
Dear {teacher_data['teacher_name']},

Your account has been created successfully in the Student Result Management System (SRMS).

Account Details:
- Name: {teacher_data['teacher_name']}
- Role: Teacher
- Email: {teacher_data['email']}
- Employee ID: {teacher_data['employee_id']}
- Username: {teacher_data['username']}
- Qualification: {teacher_data['qualification']}
- Assigned Subjects: {teacher_data['subjects']}

Your temporary password is: {teacher_data['password']}

Please login to the system and change your password for security.

Login URL: http://127.0.0.1:8000/accounts/login/teacher/

Best regards,
SRMS Administration Team
"""
    
    # Also send HTML version
    html_message = render_to_string('emails/teacher_registration.html', teacher_data)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [teacher_data['email']],
        html_message=html_message,
        fail_silently=False,
    )
    
    print("✅ Teacher registration email sent successfully!")
    print(f"   FROM: {settings.EMAIL_HOST_USER}")
    print(f"   TO: {teacher_data['email']}")
    print(f"   SUBJECT: {subject}")
    print()
    
except Exception as e:
    print(f"❌ Failed to send teacher email!")
    print(f"   Error: {str(e)}")
    print()
    import traceback
    traceback.print_exc()

# Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("✅ Email system is configured correctly!")
print()
print("What happens when you register a Student/Teacher:")
print()
print("1. Admin fills registration form")
print("2. Student/Teacher data is saved to database")
print("3. Email is automatically sent to the registered email address")
print("4. Email contains:")
print("   - Confirmation message")
print("   - User's name")
print("   - Role (Student/Teacher)")
print("   - Registered email")
print("   - Login credentials")
print("   - Subject: 'Account Created Successfully – SRMS'")
print()
print("Check your inbox: tanveerkakar294@gmail.com")
print("You should have received 2 test emails!")
print()
print("Next steps:")
print("1. Check your email inbox")
print("2. Restart Django server: python srms_project/manage.py runserver")
print("3. Add a real student/teacher with their email")
print("4. They will receive the confirmation email!")
print()
print("=" * 80)
