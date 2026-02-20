#!/usr/bin/env python
"""
Direct email test using smtplib
This tests if email sending works with the provided credentials
"""

import smtplib
from email.message import EmailMessage

def test_email():
    print("=" * 60)
    print("Testing Email Sending with smtplib")
    print("=" * 60)
    
    try:
        # Create email message
        msg = EmailMessage()
        msg['Subject'] = 'Test Email from SRMS - Email Configuration Working!'
        msg['From'] = 'tanveerkakar294@gmail.com'
        msg['To'] = 'tanveerkakar294@gmail.com'  # Sending to self for testing
        
        email_body = """
Hello!

This is a test email from your Student Result Management System (SRMS).

If you receive this email, it means your email configuration is working correctly!

The system will now be able to send:
- Registration confirmation emails to students and teachers
- Password reset emails
- Account notifications

Best regards,
SRMS Team
"""
        msg.set_content(email_body)
        
        # Gmail SMTP server
        smtp_server = 'smtp.gmail.com'
        port = 587
        
        print("\n📧 Connecting to Gmail SMTP server...")
        print(f"   Server: {smtp_server}")
        print(f"   Port: {port}")
        print(f"   From: tanveerkakar294@gmail.com")
        print(f"   To: tanveerkakar294@gmail.com")
        
        # Login and send
        with smtplib.SMTP(smtp_server, port) as server:
            print("\n🔐 Starting TLS encryption...")
            server.starttls()
            
            print("🔑 Logging in...")
            server.login('tanveerkakar294@gmail.com', 'jxsnktwtwbedqlew')
            
            print("📤 Sending email...")
            server.send_message(msg)
        
        print("\n✅ SUCCESS! Email sent successfully!")
        print("\n📬 Please check your inbox at: tanveerkakar294@gmail.com")
        print("   (It may take a few seconds to arrive)")
        print("\n" + "=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Email sending failed!")
        print(f"   Error: {str(e)}")
        print("\n" + "=" * 60)
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_email()
