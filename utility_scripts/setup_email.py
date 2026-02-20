#!/usr/bin/env python
"""
Interactive Email Configuration Setup
This script will help you configure Gmail for sending emails
"""

import os
import sys

def setup_email():
    print("=" * 60)
    print("SRMS - Email Configuration Setup")
    print("=" * 60)
    print()
    
    print("This script will help you configure Gmail for sending emails.")
    print()
    
    # Check if user has Gmail credentials
    print("STEP 1: Do you have a Gmail account?")
    print("You need a Gmail account to send emails.")
    has_gmail = input("Do you have Gmail? (yes/no): ").strip().lower()
    
    if has_gmail != 'yes':
        print()
        print("❌ You need a Gmail account to send emails.")
        print("Please create one at: https://gmail.com")
        return
    
    print()
    print("STEP 2: Have you enabled 2-Step Verification?")
    print("Go to: https://myaccount.google.com/security")
    has_2fa = input("Is 2-Step Verification enabled? (yes/no): ").strip().lower()
    
    if has_2fa != 'yes':
        print()
        print("❌ You need to enable 2-Step Verification first!")
        print("1. Go to: https://myaccount.google.com/security")
        print("2. Enable '2-Step Verification'")
        print("3. Run this script again")
        return
    
    print()
    print("STEP 3: Generate App Password")
    print("1. Go to: https://myaccount.google.com/apppasswords")
    print("2. Select: Mail → Windows Computer")
    print("3. Click: Generate")
    print("4. Copy the 16-character password")
    print()
    
    # Get Gmail address
    gmail = input("Enter your Gmail address: ").strip()
    if not gmail or '@gmail.com' not in gmail:
        print("❌ Invalid Gmail address!")
        return
    
    # Get App Password
    print()
    app_password = input("Enter your App Password (16 characters, no spaces): ").strip()
    app_password = app_password.replace(' ', '')  # Remove any spaces
    
    if len(app_password) != 16:
        print(f"❌ App Password should be 16 characters! You entered {len(app_password)} characters.")
        return
    
    print()
    print("=" * 60)
    print("Configuration Summary:")
    print("=" * 60)
    print(f"Gmail: {gmail}")
    print(f"App Password: {'*' * 16} (hidden)")
    print()
    
    confirm = input("Is this correct? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Configuration cancelled.")
        return
    
    # Read settings file
    settings_path = os.path.join('srms_project', 'srms_project', 'settings.py')
    
    if not os.path.exists(settings_path):
        print(f"❌ Settings file not found: {settings_path}")
        return
    
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace email configuration
    new_config = f"""# Email Configuration - Gmail SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '{gmail}'
EMAIL_HOST_PASSWORD = '{app_password}'
DEFAULT_FROM_EMAIL = 'SRMS - Student Result Management System <{gmail}>'
"""
    
    # Find and replace email configuration section
    if 'EMAIL_BACKEND' in content:
        # Find the email configuration section
        lines = content.split('\n')
        new_lines = []
        skip_until_blank = False
        email_section_found = False
        
        for i, line in enumerate(lines):
            if '# Email Configuration' in line and not email_section_found:
                # Found email configuration section
                email_section_found = True
                skip_until_blank = True
                new_lines.append(new_config.rstrip())
                continue
            
            if skip_until_blank:
                # Skip lines until we find a blank line or new section
                if line.strip() == '' or (line.strip().startswith('#') and 'Email' not in line):
                    skip_until_blank = False
                    new_lines.append(line)
                continue
            
            new_lines.append(line)
        
        content = '\n'.join(new_lines)
    else:
        # Add email configuration at the end
        content += '\n\n' + new_config
    
    # Write back to file
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("=" * 60)
    print("✅ Email Configuration Successful!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Restart your Django server:")
    print("   - Stop: Press Ctrl+C")
    print("   - Start: python srms_project/manage.py runserver")
    print()
    print("2. Test by adding a student with a real email address")
    print()
    print("3. Check the email inbox (and spam folder)")
    print()
    print("✅ Emails will now be sent to real addresses!")
    print()

if __name__ == '__main__':
    try:
        setup_email()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
