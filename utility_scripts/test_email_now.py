#!/usr/bin/env python
"""
Test Email Sending - Verify Gmail Configuration
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

print("=" * 60)
print("TESTING EMAIL CONFIGURATION")
print("=" * 60)
print()

print("Email Configuration:")
print(f"  Backend: {settings.EMAIL_BACKEND}")
print(f"  Host: {settings.EMAIL_HOST}")
print(f"  Port: {settings.EMAIL_PORT}")
print(f"  User: {settings.EMAIL_HOST_USER}")
print(f"  From: {settings.DEFAULT_FROM_EMAIL}")
print()

print("Sending test email...")
print()

try:
    send_mail(
        'Test Email - SRMS',
        'This is a test email from SRMS. If you receive this, email configuration is working!',
        settings.DEFAULT_FROM_EMAIL,
        ['tanveerkakar294@gmail.com'],  # Send to your email
        fail_silently=False,
    )
    
    print("✅ SUCCESS!")
    print()
    print("Email sent successfully to: tanveerkakar294@gmail.com")
    print()
    print("Check your inbox (and spam folder)!")
    print()
    print("If you received the email, the configuration is working correctly.")
    print("Now when you add students/teachers, they will receive emails!")
    print()
    
except Exception as e:
    print("❌ FAILED!")
    print()
    print(f"Error: {str(e)}")
    print()
    print("Troubleshooting:")
    print("1. Check if 2-Step Verification is enabled on Gmail")
    print("2. Verify App Password is correct (no spaces)")
    print("3. Check internet connection")
    print("4. Make sure Gmail account is active")
    print()
    import traceback
    traceback.print_exc()

print("=" * 60)
