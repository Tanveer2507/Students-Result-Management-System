#!/usr/bin/env python
"""Quick Email Test"""
import smtplib
from email.message import EmailMessage

print("Testing email sending...")

try:
    msg = EmailMessage()
    msg['Subject'] = 'Test - Account Created Successfully'
    msg['From'] = 'tanveerkakar294@gmail.com'
    msg['To'] = 'tanveerkakar294@gmail.com'
    msg.set_content('Test email from SRMS. If you receive this, email is working!')
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('tanveerkakar294@gmail.com', 'jxsnktwtwbedqlew')
        server.send_message(msg)
    
    print("✅ Email sent successfully!")
    print("Check inbox: tanveerkakar294@gmail.com")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
