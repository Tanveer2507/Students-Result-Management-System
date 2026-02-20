#!/usr/bin/env python
"""
Final Email Test - Complete Verification
Tests both direct SMTP and Django email system
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
import smtplib
from email.message import EmailMessage

print("=" * 70)
print("FINAL EMAIL CONFIGURATION TEST")
print("=" * 70)
print()

# Test 1: Direct SMTP Test (Your Code Style)
print("TEST 1: Direct SMTP Email (Using smtplib)")
print("-" * 70)
print()

try:
    msg = EmailMessage()
    msg['Subject'] = 'Test 1: Direct SMTP - Account Created Successfully'
    msg['From'] = 'tanveerkakar294@gmail.com'
    msg['To'] = 'tanveerkakar294@gmail.com'
    
    msg.set_content("""
Hello!

This is Test 1 - Direct SMTP Email Test

Your account has been created successfully in SRMS.

Account Details:
- Username: testuser
- Email: tanveerkakar294@gmail.com
- Status: Active

Best regards,
SRMS Team
""")
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('tanveerkakar294@gmail.com', 'jxsn ktwt wbed qlew')
        server.send_message(msg)
    
    print("✅ Test 1 PASSED - Direct SMTP email sent!")
    print()
    
except Exception as e:
    print(f"❌ Test 1 FAILED - Error: {str(e)}")
    print()

# Test 2: Django Email System Test
print("TEST 2: Django Email System")
print("-" * 70)
print()

try:
    send_mail(
        'Test 2: Django Email - Account Created Successfully',
        'This is Test 2 - Django email system test. Your account has been created successfully!',
        settings.DEFAULT_FROM_EMAIL,
        ['tanveerkakar294@gmail.com'],
        fail_silently=False,
    )
    
    print("✅ Test 2 PASSED - Django email sent!")
    print()
    
except Exception as e:
    print(f"❌ Test 2 FAILED - Error: {str(e)}")
    print()

# Test 3: HTML Email Template Test (Student Registration Style)
print("TEST 3: HTML Email Template (Student Registration)")
print("-" * 70)
print()

try:
    html_message = render_to_string('emails/student_registration.html', {
        'student_name': 'Test Student',
        'roll_number': 'TEST001',
        'username': 'teststudent',
        'email': 'tanveerkakar294@gmail.com',
        'password': 'test123',
        'class_name': 'Class 10 - A',
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        'Test 3: Student Registration - Account Created Successfully',
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        ['tanveerkakar294@gmail.com'],
        html_message=html_message,
        fail_silently=False,
    )
    
    print("✅ Test 3 PASSED - HTML email sent!")
    print()
    
except Exception as e:
    print(f"❌ Test 3 FAILED - Error: {str(e)}")
    print()

# Test 4: Teacher Registration Email Test
print("TEST 4: HTML Email Template (Teacher Registration)")
print("-" * 70)
print()

try:
    html_message = render_to_string('emails/teacher_registration.html', {
        'teacher_name': 'Test Teacher',
        'employee_id': 'EMP001',
        'username': 'testteacher',
        'email': 'tanveerkakar294@gmail.com',
        'password': 'test123',
        'qualification': 'M.Sc',
        'subjects': 'Mathematics, Physics',
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        'Test 4: Teacher Registration - Account Created Successfully',
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        ['tanveerkakar294@gmail.com'],
        html_message=html_message,
        fail_silently=False,
    )
    
    print("✅ Test 4 PASSED - Teacher HTML email sent!")
    print()
    
except Exception as e:
    print(f"❌ Test 4 FAILED - Error: {str(e)}")
    print()

# Summary
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print()
print("Email Configuration:")
print(f"  From: {settings.EMAIL_HOST_USER}")
print(f"  Backend: {settings.EMAIL_BACKEND}")
print(f"  Host: {settings.EMAIL_HOST}")
print(f"  Port: {settings.EMAIL_PORT}")
print()
print("Check your inbox: tanveerkakar294@gmail.com")
print("You should receive 4 test emails!")
print()
print("If all tests passed:")
print("✅ Student registration emails will work")
print("✅ Teacher registration emails will work")
print("✅ Forgot password emails will work")
print()
print("Next steps:")
print("1. Check your email inbox")
print("2. Restart Django server")
print("3. Add a student/teacher")
print("4. They will receive welcome email!")
print()
print("=" * 70)
