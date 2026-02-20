#!/usr/bin/env python
"""
Direct Email Test using smtplib
Testing email sending with your credentials
"""

import smtplib
from email.message import EmailMessage

print("=" * 60)
print("TESTING DIRECT EMAIL SENDING")
print("=" * 60)
print()

# Create email
msg = EmailMessage()
msg['Subject'] = 'Test Email from SRMS - Account Created Successfully'
msg['From'] = 'tanveerkakar294@gmail.com'
msg['To'] = 'tanveerkakar294@gmail.com'  # Sending to yourself for testing

# Email content
email_body = """
Hello!

Your account has been created successfully in SRMS (Student Result Management System).

This is a test email to verify that email sending is working correctly.

Account Details:
- Username: testuser
- Email: tanveerkakar294@gmail.com
- Status: Active

You can now login to the system.

Best regards,
SRMS Administration Team
"""

msg.set_content(email_body)

# Gmail SMTP server
smtp_server = 'smtp.gmail.com'
port = 587

print("Sending email...")
print(f"From: tanveerkakar294@gmail.com")
print(f"To: tanveerkakar294@gmail.com")
print(f"Subject: {msg['Subject']}")
print()

try:
    # Login and send
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()  # Secure connection
        server.login('tanveerkakar294@gmail.com', 'jxsn ktwt wbed qlew')
        server.send_message(msg)
    
    print("✅ Email sent successfully!")
    print()
    print("Check your inbox: tanveerkakar294@gmail.com")
    print("(Also check spam folder)")
    print()
    print("If you received this email, the configuration is working!")
    print("Now student/teacher registration emails will also work!")
    
except Exception as e:
    print("❌ Email sending failed!")
    print(f"Error: {str(e)}")
    print()
    print("Troubleshooting:")
    print("1. Check internet connection")
    print("2. Verify Gmail credentials")
    print("3. Make sure 2-Step Verification is enabled")
    print("4. Check if App Password is correct")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
