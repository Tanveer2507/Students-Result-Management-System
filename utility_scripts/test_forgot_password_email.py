#!/usr/bin/env python
"""
Test script to verify forgot password email functionality
Run this to test if emails are being sent correctly
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'srms_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

print("=" * 60)
print("FORGOT PASSWORD EMAIL TEST")
print("=" * 60)
print()

# Check email configuration
print("1. Checking Email Configuration...")
print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
if hasattr(settings, 'EMAIL_HOST'):
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
if hasattr(settings, 'EMAIL_HOST_USER'):
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print()

# Get a test user
print("2. Finding a test user...")
users = User.objects.all()[:5]
if not users:
    print("   ❌ No users found in database!")
    print("   Please create a user first.")
    sys.exit(1)

print(f"   Found {users.count()} users:")
for i, user in enumerate(users, 1):
    print(f"   {i}. {user.username} ({user.email})")
print()

# Select first user with email
test_user = None
for user in users:
    if user.email:
        test_user = user
        break

if not test_user:
    print("   ❌ No user with email found!")
    print("   Please add email to a user account.")
    sys.exit(1)

print(f"3. Using test user: {test_user.username} ({test_user.email})")
print()

# Generate reset token
print("4. Generating password reset token...")
token = default_token_generator.make_token(test_user)
uid = urlsafe_base64_encode(force_bytes(test_user.pk))
reset_link = f"http://127.0.0.1:8000/accounts/reset-password/{uid}/{token}/"
print(f"   Token generated: {token[:20]}...")
print(f"   UID: {uid}")
print(f"   Reset Link: {reset_link}")
print()

# Try to send email
print("5. Attempting to send password reset email...")
try:
    subject = 'Password Reset Request - SRMS (TEST)'
    html_message = render_to_string('emails/password_reset_request.html', {
        'user': test_user,
        'reset_link': reset_link,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [test_user.email],
        html_message=html_message,
        fail_silently=False,
    )
    
    print("   ✅ Email sent successfully!")
    print()
    print("=" * 60)
    print("SUCCESS!")
    print("=" * 60)
    print()
    
    if 'console' in settings.EMAIL_BACKEND.lower():
        print("📧 EMAIL BACKEND: Console")
        print("   Check your terminal/console output above.")
        print("   The email should be printed there.")
    else:
        print("📧 EMAIL BACKEND: SMTP")
        print(f"   Email sent to: {test_user.email}")
        print("   Check the inbox (and spam folder).")
    
    print()
    print("To test the reset link:")
    print(f"   Open: {reset_link}")
    print()
    
except Exception as e:
    print(f"   ❌ Email sending failed!")
    print(f"   Error: {str(e)}")
    print()
    print("=" * 60)
    print("TROUBLESHOOTING:")
    print("=" * 60)
    print()
    print("1. Check email configuration in settings.py")
    print("2. If using Gmail, verify App Password is correct")
    print("3. Check if EMAIL_BACKEND is set correctly")
    print("4. Try using console backend for testing:")
    print("   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'")
    print()
    import traceback
    traceback.print_exc()
