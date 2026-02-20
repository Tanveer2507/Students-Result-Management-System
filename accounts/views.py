from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile

def login_view(request):
    """Main login page with role selection"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/login_select.html')

def admin_login(request):
    """Admin login page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is admin or superuser
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.role == 'admin' or user.is_superuser:
                    login(request, user)
                    return redirect('dashboard')
                else:
                    messages.error(request, 'You do not have admin access. Please use the correct login page.')
            except UserProfile.DoesNotExist:
                if user.is_superuser:
                    login(request, user)
                    return redirect('dashboard')
                else:
                    messages.error(request, 'You do not have admin access.')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'accounts/admin_login.html')

def student_login(request):
    """Student login page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"[DEBUG] Student login attempt - Username: {username}")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            print(f"[DEBUG] Authentication successful for: {user.username}")
            # Check if user is student
            try:
                profile = UserProfile.objects.get(user=user)
                print(f"[DEBUG] Profile found - Role: {profile.role}")
                if profile.role == 'student':
                    login(request, user)
                    print(f"[DEBUG] Login successful, redirecting to dashboard")
                    return redirect('dashboard')
                else:
                    print(f"[DEBUG] Wrong role: {profile.role}")
                    messages.error(request, 'You do not have student access. Please use the correct login page.')
            except UserProfile.DoesNotExist:
                print(f"[DEBUG] UserProfile not found for user: {user.username}")
                messages.error(request, 'Student profile not found.')
        else:
            print(f"[DEBUG] Authentication failed for username: {username}")
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'accounts/student_login.html')

def teacher_login(request):
    """Teacher login page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is teacher
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.role == 'teacher':
                    login(request, user)
                    return redirect('dashboard')
                else:
                    messages.error(request, 'You do not have teacher access. Please use the correct login page.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Teacher profile not found.')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'accounts/teacher_login.html')

@login_required
def dashboard(request):
    print(f"[DEBUG] Dashboard view called for user: {request.user.username}")
    try:
        profile = UserProfile.objects.get(user=request.user)
        role = profile.role
        print(f"[DEBUG] User role: {role}")
    except UserProfile.DoesNotExist:
        print(f"[DEBUG] No profile found, checking if superuser")
        role = 'admin' if request.user.is_superuser else None
    
    if role == 'admin' or request.user.is_superuser:
        print(f"[DEBUG] Redirecting to admin_dashboard")
        return redirect('admin_dashboard')
    elif role == 'teacher':
        print(f"[DEBUG] Redirecting to teacher_dashboard")
        return redirect('teacher_dashboard')
    elif role == 'student':
        print(f"[DEBUG] Redirecting to student_dashboard")
        return redirect('student_dashboard')
    else:
        print(f"[DEBUG] No role assigned")
        messages.error(request, 'No role assigned')
        return redirect('login')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('login')


def student_registration(request):
    """Student self-registration page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        roll_number = request.POST.get('roll_number')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        father_name = request.POST.get('father_name')
        mother_name = request.POST.get('mother_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        # Comprehensive validation
        errors = []
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if User.objects.filter(username=username).exists():
            errors.append('Username already exists')
        
        if User.objects.filter(email=email).exists():
            errors.append('Email already registered')
        
        from students.models import Student, Class
        
        if Student.objects.filter(roll_number=roll_number).exists():
            errors.append('Roll number already exists')
        
        if Student.objects.filter(phone=phone).exists():
            errors.append('Phone number already registered')
        
        # Show all errors
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/student_registration.html')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                role='student',
                phone=phone,
                address=address
            )
            
            # Get or create default class (you can modify this)
            default_class, _ = Class.objects.get_or_create(
                name="Unassigned",
                section="Pending"
            )
            
            # Create student record
            student = Student.objects.create(
                user=user,
                roll_number=roll_number,
                student_class=default_class,
                date_of_birth=date_of_birth,
                gender=gender,
                father_name=father_name,
                mother_name=mother_name,
                phone=phone,
                address=address
            )
            
            # Send registration email using smtplib
            try:
                import smtplib
                from email.message import EmailMessage
                
                # Create email message
                msg = EmailMessage()
                msg['Subject'] = 'Account Created Successfully – SRMS'
                msg['From'] = 'admin@srms.com'
                msg['To'] = email
                
                # Email content
                email_body = f"""
Dear {first_name} {last_name},

Welcome to Student Result Management System (SRMS)!

Your Student account has been created successfully. Here are your account details:

Name: {first_name} {last_name}
Role: Student
Roll Number: {roll_number}
Class: {student.student_class}
Username: {username}
Registered Email: {email}

You can now login to the system using your username and password.

Login URL: {request.build_absolute_uri('/accounts/login/student/')}

Best regards,
SRMS Team
"""
                msg.set_content(email_body)
                
                # Send email using Gmail SMTP
                smtp_server = 'smtp.gmail.com'
                port = 587
                
                with smtplib.SMTP(smtp_server, port) as server:
                    server.starttls()
                    server.login('admin@srms.com', 'jxsnktwtwbedqlew')
                    server.send_message(msg)
                
                print(f"✅ Registration email sent successfully to {email}")
            except Exception as e:
                print(f"❌ Email sending failed: {str(e)}")
                import traceback
                traceback.print_exc()
            
            messages.success(request, 'Registration successful! You can now login. Check your email for account details.')
            return redirect('student_login')
            
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'accounts/student_registration.html')
    
    return render(request, 'accounts/student_registration.html')


def teacher_registration(request):
    """Teacher self-registration page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        teacher_email = request.POST.get('teacher_email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        employee_id = request.POST.get('employee_id')
        phone = request.POST.get('phone')
        qualification = request.POST.get('qualification')
        specialization = request.POST.get('specialization')
        experience = request.POST.get('experience')
        address = request.POST.get('address')
        
        # Comprehensive validation
        errors = []
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if User.objects.filter(username=username).exists():
            errors.append('Username already exists')
        
        if User.objects.filter(email=email).exists():
            errors.append('User email already registered')
        
        from students.models import Teacher
        
        if Teacher.objects.filter(employee_id=employee_id).exists():
            errors.append('Employee ID already exists')
        
        if Teacher.objects.filter(email=teacher_email).exists():
            errors.append('Teacher email already registered')
        
        if Teacher.objects.filter(phone=phone).exists():
            errors.append('Phone number already registered')
        
        # Show all errors
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/teacher_registration.html')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                role='teacher',
                phone=phone,
                address=address
            )
            
            # Create teacher record
            teacher = Teacher.objects.create(
                user=user,
                employee_id=employee_id,
                email=teacher_email,
                phone=phone,
                qualification=qualification,
                specialization=specialization,
                experience=experience,
                address=address
            )
            
            # Send registration email using smtplib
            try:
                import smtplib
                from email.message import EmailMessage
                
                # Create email message
                msg = EmailMessage()
                msg['Subject'] = 'Account Created Successfully – SRMS'
                msg['From'] = 'admin@srms.com'
                msg['To'] = teacher_email
                
                # Email content
                email_body = f"""
Dear {first_name} {last_name},

Welcome to Student Result Management System (SRMS)!

Your Teacher account has been created successfully. Here are your account details:

Name: {first_name} {last_name}
Role: Teacher
Employee ID: {employee_id}
Username: {username}
Registered Email: {teacher_email}
Qualification: {qualification}

You can now login to the system using your username and password.

Login URL: {request.build_absolute_uri('/accounts/login/teacher/')}

Best regards,
SRMS Team
"""
                msg.set_content(email_body)
                
                # Send email using Gmail SMTP
                smtp_server = 'smtp.gmail.com'
                port = 587
                
                with smtplib.SMTP(smtp_server, port) as server:
                    server.starttls()
                    server.login('admin@srms.com', 'jxsnktwtwbedqlew')
                    server.send_message(msg)
                
                print(f"✅ Registration email sent successfully to {teacher_email}")
            except Exception as e:
                print(f"❌ Email sending failed: {str(e)}")
                import traceback
                traceback.print_exc()
            
            messages.success(request, 'Registration successful! You can now login. Check your email for account details.')
            return redirect('teacher_login')
            
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'accounts/teacher_registration.html')
    
    return render(request, 'accounts/teacher_registration.html')


# Forgot Password Views - Separate for Admin, Teachers, Students
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import smtplib
from email.message import EmailMessage

def admin_forgot_password(request):
    """Admin forgot password page"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        print(f"[ADMIN FORGOT PASSWORD] Email submitted: {email}")
        
        try:
            user = User.objects.get(email=email)
            print(f"[ADMIN FORGOT PASSWORD] User found: {user.username}")
            
            # Check if user is admin
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.role != 'admin' and not user.is_superuser:
                    messages.error(request, 'This email is not registered as an admin account.')
                    return render(request, 'accounts/admin_forgot_password.html')
            except UserProfile.DoesNotExist:
                if not user.is_superuser:
                    messages.error(request, 'This email is not registered as an admin account.')
                    return render(request, 'accounts/admin_forgot_password.html')
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link
            reset_link = request.build_absolute_uri(
                f'/reset-password/{uid}/{token}/'
            )
            
            print(f"[ADMIN FORGOT PASSWORD] Reset link generated: {reset_link}")
            
            # Send email using smtplib
            try:
                msg = EmailMessage()
                msg['Subject'] = 'Password Reset Request - SRMS Admin'
                msg['From'] = 'admin@srms.com'
                msg['To'] = email
                
                email_body = f"""
Dear {user.get_full_name() or user.username},

You have requested to reset your password for your SRMS Admin account.

Click the link below to reset your password:
{reset_link}

This link will expire in 24 hours.

If you did not request this password reset, please ignore this email.

Best regards,
SRMS Team
"""
                msg.set_content(email_body)
                
                smtp_server = 'smtp.gmail.com'
                port = 587
                
                with smtplib.SMTP(smtp_server, port) as server:
                    server.starttls()
                    server.login('admin@srms.com', 'jxsnktwtwbedqlew')
                    server.send_message(msg)
                
                print(f"[ADMIN FORGOT PASSWORD] ✅ Email sent successfully!")
                messages.success(request, f'Password reset link has been sent to {email}. Please check your email.')
            except Exception as e:
                print(f"[ADMIN FORGOT PASSWORD] ❌ Email sending failed: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.warning(request, f'Password reset link generated but email failed to send. Error: {str(e)}')
            
            return redirect('admin_login')
            
        except User.DoesNotExist:
            print(f"[ADMIN FORGOT PASSWORD] ❌ No user found with email: {email}")
            messages.error(request, 'No admin account found with this email address.')
    
    return render(request, 'accounts/admin_forgot_password.html')

def teacher_forgot_password(request):
    """Teacher forgot password page"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        print(f"[TEACHER FORGOT PASSWORD] Email submitted: {email}")
        
        try:
            user = User.objects.get(email=email)
            print(f"[TEACHER FORGOT PASSWORD] User found: {user.username}")
            
            # Check if user is teacher
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.role != 'teacher':
                    messages.error(request, 'This email is not registered as a teacher account.')
                    return render(request, 'accounts/teacher_forgot_password.html')
            except UserProfile.DoesNotExist:
                messages.error(request, 'This email is not registered as a teacher account.')
                return render(request, 'accounts/teacher_forgot_password.html')
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link
            reset_link = request.build_absolute_uri(
                f'/reset-password/{uid}/{token}/'
            )
            
            print(f"[TEACHER FORGOT PASSWORD] Reset link generated: {reset_link}")
            
            # Send email using smtplib
            try:
                msg = EmailMessage()
                msg['Subject'] = 'Password Reset Request - SRMS Teacher'
                msg['From'] = 'admin@srms.com'
                msg['To'] = email
                
                email_body = f"""
Dear {user.get_full_name() or user.username},

You have requested to reset your password for your SRMS Teacher account.

Click the link below to reset your password:
{reset_link}

This link will expire in 24 hours.

If you did not request this password reset, please ignore this email.

Best regards,
SRMS Team
"""
                msg.set_content(email_body)
                
                smtp_server = 'smtp.gmail.com'
                port = 587
                
                with smtplib.SMTP(smtp_server, port) as server:
                    server.starttls()
                    server.login('admin@srms.com', 'jxsnktwtwbedqlew')
                    server.send_message(msg)
                
                print(f"[TEACHER FORGOT PASSWORD] ✅ Email sent successfully!")
                messages.success(request, f'Password reset link has been sent to {email}. Please check your email.')
            except Exception as e:
                print(f"[TEACHER FORGOT PASSWORD] ❌ Email sending failed: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.warning(request, f'Password reset link generated but email failed to send. Error: {str(e)}')
            
            return redirect('teacher_login')
            
        except User.DoesNotExist:
            print(f"[TEACHER FORGOT PASSWORD] ❌ No user found with email: {email}")
            messages.error(request, 'No teacher account found with this email address.')
    
    return render(request, 'accounts/teacher_forgot_password.html')

def student_forgot_password(request):
    """Student forgot password page"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        print(f"[STUDENT FORGOT PASSWORD] Email submitted: {email}")
        
        try:
            user = User.objects.get(email=email)
            print(f"[STUDENT FORGOT PASSWORD] User found: {user.username}")
            
            # Check if user is student
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.role != 'student':
                    messages.error(request, 'This email is not registered as a student account.')
                    return render(request, 'accounts/student_forgot_password.html')
            except UserProfile.DoesNotExist:
                messages.error(request, 'This email is not registered as a student account.')
                return render(request, 'accounts/student_forgot_password.html')
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link
            reset_link = request.build_absolute_uri(
                f'/reset-password/{uid}/{token}/'
            )
            
            print(f"[STUDENT FORGOT PASSWORD] Reset link generated: {reset_link}")
            
            # Send email using smtplib
            try:
                msg = EmailMessage()
                msg['Subject'] = 'Password Reset Request - SRMS Student'
                msg['From'] = 'admin@srms.com'
                msg['To'] = email
                
                email_body = f"""
Dear {user.get_full_name() or user.username},

You have requested to reset your password for your SRMS Student account.

Click the link below to reset your password:
{reset_link}

This link will expire in 24 hours.

If you did not request this password reset, please ignore this email.

Best regards,
SRMS Team
"""
                msg.set_content(email_body)
                
                smtp_server = 'smtp.gmail.com'
                port = 587
                
                with smtplib.SMTP(smtp_server, port) as server:
                    server.starttls()
                    server.login('admin@srms.com', 'jxsnktwtwbedqlew')
                    server.send_message(msg)
                
                print(f"[STUDENT FORGOT PASSWORD] ✅ Email sent successfully!")
                messages.success(request, f'Password reset link has been sent to {email}. Please check your email.')
            except Exception as e:
                print(f"[STUDENT FORGOT PASSWORD] ❌ Email sending failed: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.warning(request, f'Password reset link generated but email failed to send. Error: {str(e)}')
            
            return redirect('student_login')
            
        except User.DoesNotExist:
            print(f"[STUDENT FORGOT PASSWORD] ❌ No user found with email: {email}")
            messages.error(request, 'No student account found with this email address.')
    
    return render(request, 'accounts/student_forgot_password.html')

def forgot_password(request):
    """Generic forgot password page - redirects to role selection"""
    return redirect('login')

def reset_password(request, uidb64, token):
    """Reset password page - user creates new password"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 and password2:
                if password1 == password2:
                    # Set new password
                    user.set_password(password1)
                    user.save()
                    
                    # Send confirmation email using smtplib
                    try:
                        msg = EmailMessage()
                        msg['Subject'] = 'Password Changed Successfully - SRMS'
                        msg['From'] = 'admin@srms.com'
                        msg['To'] = user.email
                        
                        email_body = f"""
Dear {user.get_full_name() or user.username},

Your password has been changed successfully!

If you did not make this change, please contact the administrator immediately.

Best regards,
SRMS Team
"""
                        msg.set_content(email_body)
                        
                        smtp_server = 'smtp.gmail.com'
                        port = 587
                        
                        with smtplib.SMTP(smtp_server, port) as server:
                            server.starttls()
                            server.login('admin@srms.com', 'jxsnktwtwbedqlew')
                            server.send_message(msg)
                        
                        print(f"✅ Password change confirmation email sent to {user.email}")
                    except Exception as e:
                        print(f"❌ Email sending failed: {str(e)}")
                        import traceback
                        traceback.print_exc()
                    
                    messages.success(request, 'Your password has been reset successfully! You can now login with your new password.')
                    return redirect('login')
                else:
                    messages.error(request, 'Passwords do not match.')
            else:
                messages.error(request, 'Please enter both password fields.')
        
        return render(request, 'accounts/reset_password.html', {'validlink': True})
    else:
        messages.error(request, 'This password reset link is invalid or has expired.')
        return render(request, 'accounts/reset_password.html', {'validlink': False})


# Website Pages
def home(request):
    """Home page"""
    from students.models import Student, Teacher, Class
    from results.models import Result
    
    context = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_classes': Class.objects.count(),
        'total_results': Result.objects.filter(published=True).count(),
    }
    return render(request, 'home.html', context)

def about(request):
    """About page"""
    return render(request, 'about.html')

def features(request):
    """Features page"""
    return render(request, 'features.html')

def contact(request):
    """Contact page with form handling"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Validate form data
        if not all([name, email, subject, message]):
            messages.error(request, 'All fields are required!')
            return render(request, 'contact.html')
        
        # Send email notification
        try:
            import smtplib
            from email.message import EmailMessage
            
            # Create email message
            msg = EmailMessage()
            msg['Subject'] = f'SRMS Contact Form: {subject}'
            msg['From'] = 'admin@srms.com'
            msg['To'] = 'admin@srms.com'
            msg['Reply-To'] = email
            
            # Email content
            email_body = f"""
New Contact Form Submission - SRMS

From: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
This message was sent from the SRMS Contact Form.
Reply directly to this email to respond to {name}.
"""
            msg.set_content(email_body)
            
            # Send email using Gmail SMTP
            smtp_server = 'smtp.gmail.com'
            port = 587
            
            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls()
                server.login('admin@srms.com', 'jxsnktwtwbedqlew')
                server.send_message(msg)
            
            messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            return redirect('contact')
        except Exception as e:
            messages.error(request, f'Failed to send message. Please try again later.')
            print(f"Contact form email error: {str(e)}")
    
    return render(request, 'contact.html')

