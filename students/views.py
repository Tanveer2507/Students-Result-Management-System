from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .models import Student, Teacher, Class, Subject
from accounts.models import UserProfile
from results.models import Marks, Result
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
import csv
from datetime import datetime

# Test view for debugging actions
@login_required
def test_actions(request):
    """Test view to debug result actions"""
    results = Result.objects.all().select_related('student__user')[:5]
    return render(request, 'students/test_actions.html', {'results': results})

@login_required
def admin_dashboard(request):
    # Get all statistics
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_classes = Class.objects.count()
    total_subjects = Subject.objects.count()
    
    # Get recent data (ordered by roll_number and employee_id for consistency)
    recent_students = Student.objects.select_related('user', 'student_class').order_by('roll_number')[:5]
    recent_teachers = Teacher.objects.select_related('user').order_by('employee_id')[:5]
    
    # Get published results count
    published_results = Result.objects.filter(published=True).count()
    
    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classes': total_classes,
        'total_subjects': total_subjects,
        'published_results': published_results,
        'recent_students': recent_students,
        'recent_teachers': recent_teachers,
    }
    return render(request, 'students/admin_dashboard.html', context)

@login_required
def teacher_dashboard(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
        subjects = teacher.subjects.all()
        
        # Get all classes where teacher teaches
        classes = set([subject.class_assigned for subject in subjects])
        students = Student.objects.filter(student_class__in=classes).order_by('roll_number')
        
        # Get marks entered by this teacher
        marks_entered = Marks.objects.filter(subject__in=subjects).count()
        
        # Get recent marks
        recent_marks = Marks.objects.filter(subject__in=subjects).select_related('student__user', 'subject').order_by('-created_at')[:5]
        
        context = {
            'teacher': teacher,
            'subjects': subjects,
            'total_subjects': subjects.count(),
            'total_students': students.count(),
            'total_classes': len(classes),
            'marks_entered': marks_entered,
            'recent_marks': recent_marks,
            'students': students[:10],  # Show first 10 students
        }
        return render(request, 'students/teacher_dashboard.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found')
        return redirect('login')

@login_required
def student_dashboard(request):
    print(f"[DEBUG] Student dashboard called for user: {request.user.username}")
    try:
        student = Student.objects.get(user=request.user)
        print(f"[DEBUG] Student found: {student.roll_number}")
        marks = Marks.objects.filter(student=student).select_related('subject')
        print(f"[DEBUG] Marks count: {marks.count()}")
        
        try:
            result = Result.objects.get(student=student, published=True)
            print(f"[DEBUG] Result found")
        except Result.DoesNotExist:
            result = None
            print(f"[DEBUG] No result found")
        
        # Calculate statistics
        total_subjects = marks.count()
        passed_subjects = sum(1 for m in marks if m.marks_obtained >= m.subject.pass_marks)
        failed_subjects = total_subjects - passed_subjects
        
        # Calculate total max marks
        total_max_marks = sum(m.subject.max_marks for m in marks) if marks.exists() else 0
        
        # Get active announcements
        try:
            announcements = get_active_announcements('students')
        except Exception as e:
            print(f"[DEBUG] Error getting announcements: {e}")
            announcements = []
        
        context = {
            'student': student,
            'marks': marks,
            'result': result,
            'total_subjects': total_subjects,
            'passed_subjects': passed_subjects,
            'failed_subjects': failed_subjects,
            'total_max_marks': total_max_marks,
            'announcements': announcements,
        }
        print(f"[DEBUG] Rendering student dashboard template")
        return render(request, 'students/student_dashboard.html', context)
    except Student.DoesNotExist:
        print(f"[DEBUG] Student record not found for user: {request.user.username}")
        messages.error(request, 'Student profile not found. Please contact administrator.')
        return redirect('login')
    except Exception as e:
        print(f"[DEBUG] Unexpected error in student dashboard: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('login')

@login_required
def student_list(request):
    students = Student.objects.all().select_related('user', 'student_class').order_by('roll_number')
    return render(request, 'students/student_list.html', {'students': students})

@login_required
def add_student(request):
    if request.method == 'POST':
        # Create user
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create user profile
        UserProfile.objects.create(user=user, role='student')
        
        # Create student
        Student.objects.create(
            user=user,
            roll_number=request.POST.get('roll_number'),
            student_class_id=request.POST.get('class_id'),
            date_of_birth=request.POST.get('date_of_birth'),
            gender=request.POST.get('gender'),
            father_name=request.POST.get('father_name'),
            mother_name=request.POST.get('mother_name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address')
        )
        
        messages.success(request, 'Student added successfully')
        return redirect('student_list')
    
    classes = Class.objects.all()
    return render(request, 'students/add_student.html', {'classes': classes})

@login_required
def class_list(request):
    classes = Class.objects.all()
    return render(request, 'students/class_list.html', {'classes': classes})

@login_required
def add_class(request):
    if request.method == 'POST':
        Class.objects.create(
            name=request.POST.get('name'),
            section=request.POST.get('section')
        )
        messages.success(request, 'Class added successfully')
        return redirect('class_list')
    return render(request, 'students/add_class.html')

@login_required
def subject_list(request):
    subjects = Subject.objects.all().select_related('class_assigned')
    return render(request, 'students/subject_list.html', {'subjects': subjects})

@login_required
def add_subject(request):
    if request.method == 'POST':
        Subject.objects.create(
            name=request.POST.get('name'),
            code=request.POST.get('code'),
            class_assigned_id=request.POST.get('class_id'),
            max_marks=request.POST.get('max_marks'),
            pass_marks=request.POST.get('pass_marks')
        )
        messages.success(request, 'Subject added successfully')
        return redirect('subject_list')
    
    classes = Class.objects.all()
    return render(request, 'students/add_subject.html', {'classes': classes})


@login_required
def student_profile(request):
    try:
        student = Student.objects.get(user=request.user)
        
        # Get academic data
        marks = Marks.objects.filter(student=student)
        total_subjects = marks.count()
        
        # Get result if exists
        try:
            result = Result.objects.get(student=student, published=True)
        except Result.DoesNotExist:
            result = None
        
        context = {
            'student': student,
            'total_subjects': total_subjects,
            'result': result,
        }
        return render(request, 'students/student_profile.html', context)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('login')

@login_required
def edit_student_profile(request):
    try:
        student = Student.objects.get(user=request.user)
        
        if request.method == 'POST':
            # Check if user wants to remove profile picture
            if 'remove_picture' in request.POST:
                if student.profile_picture:
                    # Delete the file from storage
                    student.profile_picture.delete(save=False)
                    student.profile_picture = None
                    student.save()
                    messages.success(request, 'Profile picture removed successfully!')
                    return redirect('edit_student_profile')
            
            # Update user information
            user = request.user
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()
            
            # Update student information
            student.phone = request.POST.get('phone')
            student.address = request.POST.get('address')
            student.father_name = request.POST.get('father_name')
            student.mother_name = request.POST.get('mother_name')
            
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                # Delete old picture if exists
                if student.profile_picture:
                    student.profile_picture.delete(save=False)
                student.profile_picture = request.FILES['profile_picture']
            
            student.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('student_profile')
        
        return render(request, 'students/edit_student_profile.html', {'student': student})
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('login')

@login_required
def student_marks_detail(request):
    try:
        student = Student.objects.get(user=request.user)
        marks = Marks.objects.filter(student=student).select_related('subject').order_by('subject__name')
        
        # Calculate subject-wise statistics
        marks_data = []
        passed_count = 0
        failed_count = 0
        total_percentage = 0
        
        for mark in marks:
            percentage = (mark.marks_obtained / mark.subject.max_marks) * 100
            status = 'Pass' if mark.marks_obtained >= mark.subject.pass_marks else 'Fail'
            marks_data.append({
                'mark': mark,
                'percentage': round(percentage, 2),
                'status': status
            })
            
            if status == 'Pass':
                passed_count += 1
            else:
                failed_count += 1
            total_percentage += percentage
        
        # Calculate average percentage
        average_percentage = round(total_percentage / len(marks_data), 2) if marks_data else 0
        
        context = {
            'student': student,
            'marks_data': marks_data,
            'passed_count': passed_count,
            'failed_count': failed_count,
            'average_percentage': average_percentage,
        }
        return render(request, 'students/student_marks_detail.html', context)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('login')

@login_required
def student_result_detail(request):
    try:
        student = Student.objects.get(user=request.user)
        marks = Marks.objects.filter(student=student).select_related('subject')
        
        try:
            result = Result.objects.get(student=student, published=True)
        except Result.DoesNotExist:
            result = None
        
        context = {
            'student': student,
            'marks': marks,
            'result': result,
        }
        return render(request, 'students/student_result_detail.html', context)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('login')

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match')
        elif len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters')
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Password changed successfully! Please login again.')
            return redirect('login')
    
    return render(request, 'students/change_password.html')


@login_required
def teacher_students_list(request):
    """Teacher view of students in their classes"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        # Get all classes where teacher teaches
        subjects = teacher.subjects.all()
        classes = set([subject.class_assigned for subject in subjects])
        students = Student.objects.filter(student_class__in=classes).select_related('user', 'student_class').order_by('roll_number')
        
        context = {
            'teacher': teacher,
            'students': students,
            'subjects': subjects,
        }
        return render(request, 'students/teacher_students_list.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found')
        return redirect('login')

@login_required
def teacher_enter_marks(request):
    """Teacher can enter marks for their subjects"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        subjects = teacher.subjects.all()
        
        if request.method == 'POST':
            student_id = request.POST.get('student_id')
            subject_id = request.POST.get('subject_id')
            marks_obtained = request.POST.get('marks_obtained')
            exam_date = request.POST.get('exam_date')
            
            # Verify teacher teaches this subject
            if not subjects.filter(id=subject_id).exists():
                messages.error(request, 'You are not authorized to enter marks for this subject')
                return redirect('teacher_enter_marks')
            
            student = get_object_or_404(Student, id=student_id)
            subject = get_object_or_404(Subject, id=subject_id)
            
            marks, created = Marks.objects.update_or_create(
                student=student,
                subject=subject,
                defaults={
                    'marks_obtained': marks_obtained,
                    'exam_date': exam_date
                }
            )
            
            if created:
                messages.success(request, f'Marks entered successfully for {student.user.get_full_name()}')
            else:
                messages.success(request, f'Marks updated successfully for {student.user.get_full_name()}')
            
            return redirect('teacher_enter_marks')
        
        # Get students from classes where teacher teaches
        classes = set([subject.class_assigned for subject in subjects])
        students = Student.objects.filter(student_class__in=classes).order_by('roll_number')
        
        context = {
            'teacher': teacher,
            'subjects': subjects,
            'students': students,
        }
        return render(request, 'students/teacher_enter_marks.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found')
        return redirect('login')

@login_required
def teacher_view_marks(request):
    """Teacher can view marks they have entered"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        subjects = teacher.subjects.all()
        marks = Marks.objects.filter(subject__in=subjects).select_related('student__user', 'subject').order_by('-created_at')
        
        context = {
            'teacher': teacher,
            'marks': marks,
            'subjects': subjects,
        }
        return render(request, 'students/teacher_view_marks.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found')
        return redirect('login')

@login_required
def teacher_profile(request):
    """Teacher profile view"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        subjects = teacher.subjects.all()
        
        context = {
            'teacher': teacher,
            'subjects': subjects,
        }
        return render(request, 'students/teacher_profile.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found')
        return redirect('login')

@login_required
def teacher_edit_profile(request):
    """Teacher can edit their profile"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        
        if request.method == 'POST':
            # Check if user wants to remove profile picture
            if 'remove_picture' in request.POST:
                if teacher.profile_picture:
                    teacher.profile_picture.delete(save=False)
                    teacher.profile_picture = None
                    teacher.save()
                    messages.success(request, 'Profile picture removed successfully!')
                    return redirect('teacher_edit_profile')
            
            # Update user information
            user = request.user
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()
            
            # Update teacher information
            teacher.phone = request.POST.get('phone')
            teacher.qualification = request.POST.get('qualification')
            teacher.specialization = request.POST.get('specialization')
            teacher.experience = request.POST.get('experience')
            teacher.address = request.POST.get('address')
            
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                if teacher.profile_picture:
                    teacher.profile_picture.delete(save=False)
                teacher.profile_picture = request.FILES['profile_picture']
            
            teacher.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('teacher_profile')
        
        return render(request, 'students/teacher_edit_profile.html', {'teacher': teacher})
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found')
        return redirect('login')


# Admin Management Views

@login_required
def admin_manage_students(request):
    """Admin view to manage all students"""
    students = Student.objects.all().select_related('user', 'student_class').order_by('roll_number')
    
    # Get all classes for filter
    classes = Class.objects.all().order_by('name', 'section')
    
    # Filter by class
    class_filter = request.GET.get('class', '')
    if class_filter:
        students = students.filter(student_class_id=class_filter)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            user__first_name__icontains=search_query
        ) | students.filter(
            user__last_name__icontains=search_query
        ) | students.filter(
            roll_number__icontains=search_query
        )
    
    # Export to CSV
    if request.GET.get('export') == 'csv':
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Roll Number', 'First Name', 'Last Name', 'Class', 'Email', 'Phone', 'Father Name', 'Mother Name', 'Address', 'Date of Birth', 'Gender'])
        
        for student in students:
            writer.writerow([
                student.roll_number,
                student.user.first_name,
                student.user.last_name,
                str(student.student_class),
                student.user.email,
                student.phone,
                student.father_name,
                student.mother_name,
                student.address,
                student.date_of_birth,
                student.get_gender_display()
            ])
        
        return response
    
    context = {
        'students': students,
        'search_query': search_query,
        'classes': classes,
        'class_filter': class_filter,
    }
    return render(request, 'students/admin_manage_students.html', context)

@login_required
def admin_manage_teachers(request):
    """Admin view to manage all teachers"""
    teachers = Teacher.objects.all().select_related('user').order_by('employee_id')
    
    # Filter by qualification
    qualification_filter = request.GET.get('qualification', '')
    if qualification_filter:
        teachers = teachers.filter(qualification__icontains=qualification_filter)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        teachers = teachers.filter(
            user__first_name__icontains=search_query
        ) | teachers.filter(
            user__last_name__icontains=search_query
        ) | teachers.filter(
            employee_id__icontains=search_query
        )
    
    # Export to CSV
    if request.GET.get('export') == 'csv':
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="teachers_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Employee ID', 'First Name', 'Last Name', 'Email', 'Phone', 'Qualification', 'Specialization', 'Experience', 'Address', 'Subjects Count'])
        
        for teacher in teachers:
            writer.writerow([
                teacher.employee_id,
                teacher.user.first_name,
                teacher.user.last_name,
                teacher.user.email,
                teacher.phone,
                teacher.qualification,
                teacher.specialization or 'N/A',
                teacher.experience,
                teacher.address or 'N/A',
                teacher.subjects.count()
            ])
        
        return response
    
    # Get unique qualifications for filter
    qualifications = Teacher.objects.values_list('qualification', flat=True).distinct().order_by('qualification')
    
    context = {
        'teachers': teachers,
        'search_query': search_query,
        'qualifications': qualifications,
        'qualification_filter': qualification_filter,
    }
    return render(request, 'students/admin_manage_teachers.html', context)

@login_required
def admin_student_detail(request, student_id):
    """Admin view to see and edit student details"""
    student = get_object_or_404(Student, id=student_id)
    marks = Marks.objects.filter(student=student).select_related('subject')
    
    try:
        result = Result.objects.get(student=student)
    except Result.DoesNotExist:
        result = None
    
    context = {
        'student': student,
        'marks': marks,
        'result': result,
    }
    return render(request, 'students/admin_student_detail.html', context)

@login_required
def admin_teacher_detail(request, teacher_id):
    """Admin view to see and edit teacher details"""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    subjects = teacher.subjects.all()
    
    # Get classes where teacher teaches
    classes = set([subject.class_assigned for subject in subjects])
    students = Student.objects.filter(student_class__in=classes)
    
    # Get marks entered by this teacher
    marks_entered = Marks.objects.filter(subject__in=subjects).count()
    
    context = {
        'teacher': teacher,
        'subjects': subjects,
        'total_students': students.count(),
        'marks_entered': marks_entered,
    }
    return render(request, 'students/admin_teacher_detail.html', context)

@login_required
def admin_delete_student(request, student_id):
    """Admin can delete a student"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        user = student.user
        student_name = user.get_full_name()
        student.delete()
        user.delete()
        messages.success(request, f'Student {student_name} deleted successfully!')
        return redirect('admin_manage_students')
    
    return render(request, 'students/admin_confirm_delete.html', {
        'object': student,
        'object_type': 'Student',
        'cancel_url': 'admin_manage_students'
    })

@login_required
def admin_delete_teacher(request, teacher_id):
    """Admin can delete a teacher"""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        user = teacher.user
        teacher_name = user.get_full_name()
        teacher.delete()
        user.delete()
        messages.success(request, f'Teacher {teacher_name} deleted successfully!')
        return redirect('admin_manage_teachers')
    
    return render(request, 'students/admin_confirm_delete.html', {
        'object': teacher,
        'object_type': 'Teacher',
        'cancel_url': 'admin_manage_teachers'
    })

@login_required
def admin_edit_student(request, student_id):
    """Admin can edit student details"""
    student = get_object_or_404(Student, id=student_id)
    classes = Class.objects.all()
    
    if request.method == 'POST':
        # Update user
        user = student.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        
        # Update student
        student.roll_number = request.POST.get('roll_number')
        student.student_class_id = request.POST.get('class_id')
        student.phone = request.POST.get('phone')
        student.father_name = request.POST.get('father_name')
        student.mother_name = request.POST.get('mother_name')
        student.address = request.POST.get('address')
        student.save()
        
        messages.success(request, 'Student updated successfully!')
        return redirect('admin_student_detail', student_id=student.id)
    
    context = {
        'student': student,
        'classes': classes,
    }
    return render(request, 'students/admin_edit_student.html', context)

@login_required
def admin_edit_teacher(request, teacher_id):
    """Admin can edit teacher details"""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    all_subjects = Subject.objects.all()
    
    if request.method == 'POST':
        # Update user
        user = teacher.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        
        # Update teacher
        teacher.employee_id = request.POST.get('employee_id')
        teacher.phone = request.POST.get('phone')
        teacher.qualification = request.POST.get('qualification')
        teacher.specialization = request.POST.get('specialization')
        teacher.experience = request.POST.get('experience')
        teacher.address = request.POST.get('address')
        teacher.save()
        
        # Update subjects
        subject_ids = request.POST.getlist('subjects')
        teacher.subjects.set(subject_ids)
        
        messages.success(request, 'Teacher updated successfully!')
        return redirect('admin_teacher_detail', teacher_id=teacher.id)
    
    context = {
        'teacher': teacher,
        'all_subjects': all_subjects,
    }
    return render(request, 'students/admin_edit_teacher.html', context)

def admin_manage_classes(request):
    """Admin view to manage classes"""
    classes = Class.objects.all().order_by('name', 'section')

    # Filter by class name
    name_filter = request.GET.get('name', '')
    if name_filter:
        classes = classes.filter(name__icontains=name_filter)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        classes = classes.filter(
            name__icontains=search_query
        ) | classes.filter(
            section__icontains=search_query
        )

    # Export to CSV
    if request.GET.get('export') == 'csv':
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="classes_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['Class Name', 'Section', 'Total Students', 'Total Subjects'])

        for class_obj in classes:
            writer.writerow([
                class_obj.name,
                class_obj.section,
                class_obj.students.count(),
                class_obj.subjects.count()
            ])

        return response

    # Get unique class names for filter dropdown
    all_class_names = Class.objects.values_list('name', flat=True).distinct().order_by('name')

    context = {
        'classes': classes,
        'search_query': search_query,
        'all_class_names': all_class_names,
        'name_filter': name_filter,
    }
    return render(request, 'students/admin_manage_classes.html', context)


def admin_manage_subjects(request):
    """Admin view to manage subjects"""
    subjects = Subject.objects.all().select_related('class_assigned').order_by('class_assigned', 'name')

    # Filter by class
    class_filter = request.GET.get('class', '')
    if class_filter:
        subjects = subjects.filter(class_assigned__id=class_filter)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        subjects = subjects.filter(
            name__icontains=search_query
        ) | subjects.filter(
            code__icontains=search_query
        )

    # Export to CSV
    if request.GET.get('export') == 'csv':
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subjects_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['Subject Name', 'Code', 'Class', 'Max Marks', 'Pass Marks', 'Teachers Count'])

        for subject in subjects:
            writer.writerow([
                subject.name,
                subject.code,
                str(subject.class_assigned),
                subject.max_marks,
                subject.pass_marks,
                subject.teachers.count()
            ])

        return response

    # Get all classes for filter dropdown
    all_classes = Class.objects.all().order_by('name', 'section')

    context = {
        'subjects': subjects,
        'search_query': search_query,
        'all_classes': all_classes,
        'class_filter': class_filter,
    }
    return render(request, 'students/admin_manage_subjects.html', context)


@login_required
def admin_add_subject(request):
    """Admin can add a new subject"""
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        class_id = request.POST.get('class_id')
        max_marks = request.POST.get('max_marks')
        pass_marks = request.POST.get('pass_marks')
        
        # Check if subject code already exists
        if Subject.objects.filter(code=code).exists():
            messages.error(request, f'Subject code {code} already exists!')
            return render(request, 'students/admin_add_subject.html', {
                'classes': Class.objects.all()
            })
        
        # Validate pass marks
        if int(pass_marks) > int(max_marks):
            messages.error(request, 'Pass marks cannot be greater than max marks!')
            return render(request, 'students/admin_add_subject.html', {
                'classes': Class.objects.all()
            })
        
        try:
            Subject.objects.create(
                name=name,
                code=code,
                class_assigned_id=class_id,
                max_marks=max_marks,
                pass_marks=pass_marks
            )
            messages.success(request, f'Subject {name} added successfully!')
            return redirect('admin_manage_subjects')
        except Exception as e:
            messages.error(request, f'Error adding subject: {str(e)}')
    
    classes = Class.objects.all()
    return render(request, 'students/admin_add_subject.html', {'classes': classes})

@login_required
def admin_subject_detail(request, subject_id):
    """Admin view to see subject details"""
    subject = get_object_or_404(Subject, id=subject_id)
    teachers = subject.teachers.all().order_by('employee_id')
    students = Student.objects.filter(student_class=subject.class_assigned).order_by('roll_number')
    marks_count = Marks.objects.filter(subject=subject).count()
    
    context = {
        'subject': subject,
        'teachers': teachers,
        'total_students': students.count(),
        'marks_count': marks_count,
    }
    return render(request, 'students/admin_subject_detail.html', context)

@login_required
def admin_edit_subject(request, subject_id):
    """Admin can edit subject details"""
    subject = get_object_or_404(Subject, id=subject_id)
    classes = Class.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        class_id = request.POST.get('class_id')
        max_marks = request.POST.get('max_marks')
        pass_marks = request.POST.get('pass_marks')
        
        # Check if another subject with same code exists
        existing = Subject.objects.filter(code=code).exclude(id=subject_id)
        if existing.exists():
            messages.error(request, f'Subject code {code} already exists!')
            return render(request, 'students/admin_edit_subject.html', {
                'subject': subject,
                'classes': classes
            })
        
        # Validate pass marks
        if int(pass_marks) > int(max_marks):
            messages.error(request, 'Pass marks cannot be greater than max marks!')
            return render(request, 'students/admin_edit_subject.html', {
                'subject': subject,
                'classes': classes
            })
        
        try:
            subject.name = name
            subject.code = code
            subject.class_assigned_id = class_id
            subject.max_marks = max_marks
            subject.pass_marks = pass_marks
            subject.save()
            
            messages.success(request, 'Subject updated successfully!')
            return redirect('admin_subject_detail', subject_id=subject.id)
        except Exception as e:
            messages.error(request, f'Error updating subject: {str(e)}')
    
    context = {
        'subject': subject,
        'classes': classes,
    }
    return render(request, 'students/admin_edit_subject.html', context)

@login_required
def admin_delete_subject(request, subject_id):
    """Admin can delete a subject"""
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        subject_name = subject.name
        
        # Check if subject has marks
        marks_count = Marks.objects.filter(subject=subject).count()
        if marks_count > 0:
            messages.error(request, f'Cannot delete subject with {marks_count} marks records. Please delete marks first.')
            return redirect('admin_subject_detail', subject_id=subject.id)
        
        subject.delete()
        messages.success(request, f'Subject {subject_name} deleted successfully!')
        return redirect('admin_manage_subjects')
    
    context = {
        'object': subject,
        'object_type': 'Subject',
        'cancel_url': 'admin_manage_subjects',
        'teachers_count': subject.teachers.count(),
        'marks_count': Marks.objects.filter(subject=subject).count(),
    }
    return render(request, 'students/admin_confirm_delete_subject.html', context)

@login_required
def admin_manage_results(request):
    """Admin view to manage results"""
    results = Result.objects.all().select_related('student__user', 'student__student_class').order_by('student__roll_number')
    
    # Filter by class
    class_filter = request.GET.get('class', '')
    if class_filter:
        results = results.filter(student__student_class_id=class_filter)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        results = results.filter(status=status_filter)
    
    # Filter by published
    published_filter = request.GET.get('published', '')
    if published_filter == 'yes':
        results = results.filter(published=True)
    elif published_filter == 'no':
        results = results.filter(published=False)
    
    # Search by student name or roll number
    search_query = request.GET.get('search', '')
    if search_query:
        results = results.filter(
            student__user__first_name__icontains=search_query
        ) | results.filter(
            student__user__last_name__icontains=search_query
        ) | results.filter(
            student__roll_number__icontains=search_query
        )
    
    # Get all classes for filter
    classes = Class.objects.all().order_by('name', 'section')
    
    context = {
        'results': results,
        'classes': classes,
        'class_filter': class_filter,
        'status_filter': status_filter,
        'published_filter': published_filter,
        'search_query': search_query,
    }
    return render(request, 'students/admin_manage_results.html', context)

@login_required
def admin_generate_result(request):
    """Admin can generate result for a student"""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_object_or_404(Student, id=student_id)
        
        # Get all marks for the student
        marks_list = Marks.objects.filter(student=student)
        
        if not marks_list.exists():
            messages.error(request, f'No marks found for {student.user.get_full_name()}. Please enter marks first.')
            return redirect('admin_generate_result')
        
        # Calculate total marks and percentage
        total_obtained = sum([mark.marks_obtained for mark in marks_list])
        total_max = sum([mark.subject.max_marks for mark in marks_list])
        percentage = (float(total_obtained) / float(total_max)) * 100
        
        # Determine grade
        if percentage >= 90:
            grade = 'A+'
        elif percentage >= 75:
            grade = 'A'
        elif percentage >= 60:
            grade = 'B'
        elif percentage >= 50:
            grade = 'C'
        elif percentage >= 35:
            grade = 'D'
        else:
            grade = 'F'
        
        # Determine status
        status = 'Pass' if percentage >= 35 else 'Fail'
        
        # Create or update result
        result, created = Result.objects.update_or_create(
            student=student,
            defaults={
                'total_marks': total_obtained,
                'percentage': round(percentage, 2),
                'grade': grade,
                'status': status,
                'published': False  # Default to unpublished
            }
        )
        
        if created:
            messages.success(request, f'Result generated successfully for {student.user.get_full_name()}!')
        else:
            messages.success(request, f'Result updated successfully for {student.user.get_full_name()}!')
        
        return redirect('admin_result_detail', result_id=result.id)
    
    # Get students who have marks but no result or unpublished result
    students_with_marks = Student.objects.filter(marks__isnull=False).distinct().order_by('roll_number')
    
    context = {
        'students': students_with_marks,
    }
    return render(request, 'students/admin_generate_result.html', context)

@login_required
def admin_result_detail(request, result_id):
    """Admin view to see result details"""
    result = get_object_or_404(Result, id=result_id)
    marks = Marks.objects.filter(student=result.student).select_related('subject')
    
    context = {
        'result': result,
        'marks': marks,
    }
    return render(request, 'students/admin_result_detail.html', context)

@login_required
def admin_edit_result(request, result_id):
    """Admin can edit result"""
    result = get_object_or_404(Result, id=result_id)
    
    if request.method == 'POST':
        # Recalculate from marks
        marks_list = Marks.objects.filter(student=result.student)
        
        if marks_list.exists():
            total_obtained = sum([mark.marks_obtained for mark in marks_list])
            total_max = sum([mark.subject.max_marks for mark in marks_list])
            percentage = (float(total_obtained) / float(total_max)) * 100
            
            # Determine grade
            if percentage >= 90:
                grade = 'A+'
            elif percentage >= 75:
                grade = 'A'
            elif percentage >= 60:
                grade = 'B'
            elif percentage >= 50:
                grade = 'C'
            elif percentage >= 35:
                grade = 'D'
            else:
                grade = 'F'
            
            # Determine status
            status = 'Pass' if percentage >= 35 else 'Fail'
            
            result.total_marks = total_obtained
            result.percentage = round(percentage, 2)
            result.grade = grade
            result.status = status
            result.save()
            
            messages.success(request, 'Result recalculated and updated successfully!')
            return redirect('admin_result_detail', result_id=result.id)
    
    marks = Marks.objects.filter(student=result.student).select_related('subject')
    
    context = {
        'result': result,
        'marks': marks,
    }
    return render(request, 'students/admin_edit_result.html', context)

@login_required
def admin_delete_result(request, result_id):
    """Admin can delete a result"""
    result = get_object_or_404(Result, id=result_id)
    
    if request.method == 'POST':
        student_name = result.student.user.get_full_name()
        result.delete()
        messages.success(request, f'Result for {student_name} deleted successfully!')
        return redirect('admin_manage_results')
    
    context = {
        'result': result,
    }
    return render(request, 'students/admin_confirm_delete_result.html', context)

@login_required
def admin_publish_result(request, result_id):
    """Admin can publish/unpublish a result"""
    result = get_object_or_404(Result, id=result_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'publish':
            result.published = True
            result.save()
            messages.success(request, f'Result published for {result.student.user.get_full_name()}!')
        elif action == 'unpublish':
            result.published = False
            result.save()
            messages.success(request, f'Result unpublished for {result.student.user.get_full_name()}!')
        
        return redirect('admin_result_detail', result_id=result.id)
    
    return redirect('admin_manage_results')

@login_required
def admin_bulk_publish_results(request):
    """Admin can publish multiple results at once"""
    if request.method == 'POST':
        result_ids = request.POST.getlist('result_ids')
        if result_ids:
            Result.objects.filter(id__in=result_ids).update(published=True)
            messages.success(request, f'{len(result_ids)} results published successfully!')
        else:
            messages.warning(request, 'No results selected.')
        
        return redirect('admin_manage_results')
    
    return redirect('admin_manage_results')

@login_required
def admin_add_class(request):
    """Admin can add a new class"""
    if request.method == 'POST':
        name = request.POST.get('name')
        section = request.POST.get('section')
        
        # Check if class already exists
        if Class.objects.filter(name=name, section=section).exists():
            messages.error(request, f'Class {name} - {section} already exists!')
            return render(request, 'students/admin_add_class.html')
        
        try:
            Class.objects.create(
                name=name,
                section=section
            )
            messages.success(request, f'Class {name} - {section} added successfully!')
            return redirect('admin_manage_classes')
        except Exception as e:
            messages.error(request, f'Error adding class: {str(e)}')
    
    return render(request, 'students/admin_add_class.html')

@login_required
def admin_class_detail(request, class_id):
    """Admin view to see class details"""
    class_obj = get_object_or_404(Class, id=class_id)
    students = Student.objects.filter(student_class=class_obj).select_related('user').order_by('roll_number')
    subjects = Subject.objects.filter(class_assigned=class_obj)
    
    context = {
        'class_obj': class_obj,
        'students': students,
        'subjects': subjects,
    }
    return render(request, 'students/admin_class_detail.html', context)

@login_required
def admin_edit_class(request, class_id):
    """Admin can edit class details"""
    class_obj = get_object_or_404(Class, id=class_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        section = request.POST.get('section')
        
        # Check if another class with same name and section exists
        existing = Class.objects.filter(name=name, section=section).exclude(id=class_id)
        if existing.exists():
            messages.error(request, f'Class {name} - {section} already exists!')
            return render(request, 'students/admin_edit_class.html', {'class_obj': class_obj})
        
        try:
            class_obj.name = name
            class_obj.section = section
            class_obj.save()
            messages.success(request, 'Class updated successfully!')
            return redirect('admin_class_detail', class_id=class_obj.id)
        except Exception as e:
            messages.error(request, f'Error updating class: {str(e)}')
    
    return render(request, 'students/admin_edit_class.html', {'class_obj': class_obj})

@login_required
def admin_delete_class(request, class_id):
    """Admin can delete a class"""
    class_obj = get_object_or_404(Class, id=class_id)
    
    if request.method == 'POST':
        class_name = str(class_obj)
        
        # Check if class has students
        student_count = Student.objects.filter(student_class=class_obj).count()
        if student_count > 0:
            messages.error(request, f'Cannot delete class with {student_count} students. Please reassign students first.')
            return redirect('admin_class_detail', class_id=class_obj.id)
        
        class_obj.delete()
        messages.success(request, f'Class {class_name} deleted successfully!')
        return redirect('admin_manage_classes')
    
    context = {
        'object': class_obj,
        'object_type': 'Class',
        'cancel_url': 'admin_manage_classes',
        'student_count': Student.objects.filter(student_class=class_obj).count(),
        'subject_count': Subject.objects.filter(class_assigned=class_obj).count(),
    }
    return render(request, 'students/admin_confirm_delete_class.html', context)

@login_required
def admin_add_teacher(request):
    """Admin can add a new teacher"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        teacher_email = request.POST.get('teacher_email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        employee_id = request.POST.get('employee_id')
        phone = request.POST.get('phone')
        
        # Comprehensive validation
        errors = []
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            errors.append('Username already exists!')
        
        # Check if user email already exists
        if User.objects.filter(email=email).exists():
            errors.append('User email already exists!')
        
        # Check if teacher email already exists
        if Teacher.objects.filter(email=teacher_email).exists():
            errors.append('Teacher email already exists!')
        
        # Check if employee ID already exists
        if Teacher.objects.filter(employee_id=employee_id).exists():
            errors.append('Employee ID already exists!')
        
        # Check if phone number already exists
        if Teacher.objects.filter(phone=phone).exists():
            errors.append('Phone number already exists!')
        
        # If there are validation errors, show them
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'students/admin_add_teacher.html', {
                'subjects': Subject.objects.all()
            })
        
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
            UserProfile.objects.create(user=user, role='teacher')
            
            # Create teacher
            teacher = Teacher.objects.create(
                user=user,
                employee_id=employee_id,
                email=teacher_email,
                phone=phone,
                qualification=request.POST.get('qualification'),
                specialization=request.POST.get('specialization'),
                experience=request.POST.get('experience', 0),
                address=request.POST.get('address')
            )
            
            # Assign subjects
            subject_ids = request.POST.getlist('subjects')
            if subject_ids:
                teacher.subjects.set(subject_ids)
            
            # Send registration email using smtplib
            try:
                import smtplib
                from email.message import EmailMessage
                
                subject_list = ', '.join([str(s) for s in teacher.subjects.all()]) if teacher.subjects.exists() else 'None assigned yet'
                
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
Qualification: {request.POST.get('qualification')}
Assigned Subjects: {subject_list}

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
                messages.success(request, f'Teacher {first_name} {last_name} added successfully! Registration email sent to {teacher_email}')
            except Exception as e:
                # Log email error but don't fail the registration
                print(f"❌ Email sending failed: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.success(request, f'Teacher {first_name} {last_name} added successfully! (Email notification failed: {str(e)})')
            
            return redirect('admin_manage_teachers')
        except Exception as e:
            messages.error(request, f'Error adding teacher: {str(e)}')
    
    subjects = Subject.objects.all().select_related('class_assigned')
    return render(request, 'students/admin_add_teacher.html', {'subjects': subjects})

@login_required
def admin_add_student(request):
    """Admin can add a new student"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        roll_number = request.POST.get('roll_number')
        phone = request.POST.get('phone')
        
        # Comprehensive validation
        errors = []
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            errors.append('Username already exists!')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            errors.append('Email already exists!')
        
        # Check if roll number already exists
        if Student.objects.filter(roll_number=roll_number).exists():
            errors.append('Roll number already exists!')
        
        # Check if phone number already exists
        if Student.objects.filter(phone=phone).exists():
            errors.append('Phone number already exists!')
        
        # If there are validation errors, show them
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'students/admin_add_student.html', {
                'classes': Class.objects.all()
            })
        
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
            UserProfile.objects.create(user=user, role='student')
            
            # Create student
            student = Student.objects.create(
                user=user,
                roll_number=roll_number,
                student_class_id=request.POST.get('class_id'),
                date_of_birth=request.POST.get('date_of_birth'),
                gender=request.POST.get('gender'),
                father_name=request.POST.get('father_name'),
                mother_name=request.POST.get('mother_name'),
                phone=phone,
                address=request.POST.get('address')
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
                messages.success(request, f'Student {first_name} {last_name} added successfully! Registration email sent to {email}')
            except Exception as e:
                # Log email error but don't fail the registration
                print(f"❌ Email sending failed: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.success(request, f'Student {first_name} {last_name} added successfully! (Email notification failed: {str(e)})')
            
            return redirect('admin_manage_students')
        except Exception as e:
            messages.error(request, f'Error adding student: {str(e)}')
    
    classes = Class.objects.all()
    return render(request, 'students/admin_add_student.html', {'classes': classes})


# Admin Profile Management Views

@login_required
def admin_profile(request):
    """Admin profile view"""
    try:
        # Check if user is admin
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            messages.error(request, 'Access denied. Admin only.')
            return redirect('dashboard')
        
        context = {
            'profile': profile,
        }
        return render(request, 'students/admin_profile.html', context)
    except UserProfile.DoesNotExist:
        # For superuser without profile
        if request.user.is_superuser:
            # Create profile for superuser
            profile = UserProfile.objects.create(
                user=request.user,
                role='admin'
            )
            context = {
                'profile': profile,
            }
            return render(request, 'students/admin_profile.html', context)
        else:
            messages.error(request, 'Admin profile not found')
            return redirect('login')

@login_required
def admin_edit_profile(request):
    """Admin can edit their profile"""
    try:
        # Check if user is admin
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            messages.error(request, 'Access denied. Admin only.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        # For superuser without profile
        if request.user.is_superuser:
            profile = UserProfile.objects.create(
                user=request.user,
                role='admin'
            )
        else:
            messages.error(request, 'Admin profile not found')
            return redirect('login')
    
    if request.method == 'POST':
        # Update user information
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        
        # Update profile information
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('admin_profile')
    
    return render(request, 'students/admin_edit_profile.html', {'profile': profile})

@login_required
def admin_change_password(request):
    """Admin can change their password"""
    # Check if user is admin
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            messages.error(request, 'Access denied. Admin only.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            messages.error(request, 'Admin profile not found')
            return redirect('login')
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match')
        elif len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters')
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Password changed successfully! Please login again.')
            return redirect('login')
    
    return render(request, 'students/admin_change_password.html')


@login_required
def student_id_card(request):
    """Display student ID card"""
    try:
        student = Student.objects.get(user=request.user)
        context = {
            'student': student,
        }
        return render(request, 'students/student_id_card.html', context)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('login')
@login_required
def teacher_id_card(request):
    """Display teacher ID card"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        context = {
            'teacher': teacher,
        }
        return render(request, 'students/teacher_id_card.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found')
        return redirect('login')


@login_required
def student_history(request):
    """Student can view their own history"""
    try:
        student = Student.objects.get(user=request.user)
        
        # Get content types
        student_ct = ContentType.objects.get_for_model(Student)
        marks_ct = ContentType.objects.get_for_model(Marks)
        result_ct = ContentType.objects.get_for_model(Result)
        user_ct = ContentType.objects.get_for_model(User)
        
        # Get all history related to this student
        history = LogEntry.objects.filter(
            content_type__in=[student_ct, marks_ct, result_ct, user_ct],
            object_id__in=[str(student.id), str(request.user.id)]
        ).select_related('user', 'content_type').order_by('-action_time')[:50]
        
        # Also get marks history
        marks_ids = Marks.objects.filter(student=student).values_list('id', flat=True)
        marks_history = LogEntry.objects.filter(
            content_type=marks_ct,
            object_id__in=[str(mid) for mid in marks_ids]
        ).select_related('user', 'content_type').order_by('-action_time')[:50]
        
        # Combine and sort
        all_history = list(history) + list(marks_history)
        all_history.sort(key=lambda x: x.action_time, reverse=True)
        all_history = all_history[:50]  # Limit to 50 most recent
        
        # Export to CSV
        if request.GET.get('export') == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="student_history_{student.roll_number}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Date & Time', 'Action', 'Changed By', 'Object Type', 'Changes'])
            
            for entry in all_history:
                action_type = 'Added' if entry.action_flag == ADDITION else 'Changed' if entry.action_flag == CHANGE else 'Deleted'
                writer.writerow([
                    entry.action_time.strftime('%Y-%m-%d %H:%M:%S'),
                    action_type,
                    entry.user.get_full_name() or entry.user.username,
                    entry.content_type.model,
                    entry.change_message
                ])
            
            return response
        
        context = {
            'student': student,
            'history': all_history,
        }
        return render(request, 'students/student_history.html', context)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('login')

@login_required
def teacher_history(request):
    """Teacher can view their own history"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        
        # Get content types
        teacher_ct = ContentType.objects.get_for_model(Teacher)
        marks_ct = ContentType.objects.get_for_model(Marks)
        user_ct = ContentType.objects.get_for_model(User)
        
        # Get all history related to this teacher
        history = LogEntry.objects.filter(
            content_type__in=[teacher_ct, user_ct],
            object_id__in=[str(teacher.id), str(request.user.id)]
        ).select_related('user', 'content_type').order_by('-action_time')[:50]
        
        # Also get marks history entered by this teacher
        subject_ids = teacher.subjects.values_list('id', flat=True)
        marks_ids = Marks.objects.filter(subject_id__in=subject_ids).values_list('id', flat=True)
        marks_history = LogEntry.objects.filter(
            content_type=marks_ct,
            object_id__in=[str(mid) for mid in marks_ids]
        ).select_related('user', 'content_type').order_by('-action_time')[:50]
        
        # Combine and sort
        all_history = list(history) + list(marks_history)
        all_history.sort(key=lambda x: x.action_time, reverse=True)
        all_history = all_history[:50]  # Limit to 50 most recent
        
        # Export to CSV
        if request.GET.get('export') == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="teacher_history_{teacher.employee_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Date & Time', 'Action', 'Changed By', 'Object Type', 'Changes'])
            
            for entry in all_history:
                action_type = 'Added' if entry.action_flag == ADDITION else 'Changed' if entry.action_flag == CHANGE else 'Deleted'
                writer.writerow([
                    entry.action_time.strftime('%Y-%m-%d %H:%M:%S'),
                    action_type,
                    entry.user.get_full_name() or entry.user.username,
                    entry.content_type.model,
                    entry.change_message
                ])
            
            return response
        
        context = {
            'teacher': teacher,
            'history': all_history,
        }
        return render(request, 'students/teacher_history.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found')
        return redirect('login')


@login_required
def admin_id_card(request):
    """Display admin ID card"""
    return render(request, 'students/admin_id_card.html')


@login_required
def download_marksheet(request):
    """Student can download their marksheet as PDF"""
    try:
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from io import BytesIO
        from datetime import datetime
        
        student = Student.objects.get(user=request.user)
        marks = Marks.objects.filter(student=student).select_related('subject')
        
        try:
            result = Result.objects.get(student=student, published=True)
        except Result.DoesNotExist:
            messages.error(request, 'Your result has not been published yet.')
            return redirect('student_dashboard')
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        
        # Container for elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4e73df'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#4e73df'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        # Header
        elements.append(Paragraph("🎓 STUDENT RESULT MANAGEMENT SYSTEM", title_style))
        elements.append(Paragraph("Academic Marksheet", subtitle_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Student Information
        elements.append(Paragraph("Student Information", heading_style))
        
        student_data = [
            ['Name:', student.user.get_full_name(), 'Roll Number:', student.roll_number],
            ['Class:', str(student.student_class), 'Date of Birth:', student.date_of_birth.strftime('%d-%m-%Y') if student.date_of_birth else 'N/A'],
            ['Father Name:', student.father_name, 'Mother Name:', student.mother_name],
        ]
        
        student_table = Table(student_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.5*inch])
        student_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fc')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f8f9fc')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(student_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Marks Table
        elements.append(Paragraph("Academic Performance", heading_style))
        
        marks_data = [['S.No', 'Subject', 'Max Marks', 'Marks Obtained', 'Percentage', 'Status']]
        
        total_max = 0
        total_obtained = 0
        
        for idx, mark in enumerate(marks, 1):
            percentage = (mark.marks_obtained / mark.subject.max_marks) * 100
            status = 'Pass' if mark.marks_obtained >= mark.subject.pass_marks else 'Fail'
            
            marks_data.append([
                str(idx),
                mark.subject.name,
                str(mark.subject.max_marks),
                str(mark.marks_obtained),
                f'{percentage:.2f}%',
                status
            ])
            
            total_max += mark.subject.max_marks
            total_obtained += mark.marks_obtained
        
        # Add total row
        marks_data.append([
            '',
            'TOTAL',
            str(total_max),
            str(total_obtained),
            f'{result.percentage:.2f}%',
            result.status
        ])
        
        marks_table = Table(marks_data, colWidths=[0.6*inch, 2.5*inch, 1.2*inch, 1.3*inch, 1.2*inch, 1*inch])
        marks_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4e73df')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            
            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f8f9fc')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(marks_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Result Summary
        elements.append(Paragraph("Result Summary", heading_style))
        
        result_data = [
            ['Total Marks:', f'{total_obtained} / {total_max}'],
            ['Percentage:', f'{result.percentage:.2f}%'],
            ['Grade:', result.grade],
            ['Status:', result.status],
        ]
        
        result_table = Table(result_data, colWidths=[2*inch, 4*inch])
        result_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fc')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(result_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", footer_style))
        elements.append(Paragraph("This is a computer-generated document. No signature is required.", footer_style))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("© 2026 Student Result Management System | Developed by Tanveer Kakar", footer_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF from buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Create response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Marksheet_{student.roll_number}_{student.user.get_full_name().replace(" ", "_")}.pdf"'
        response.write(pdf)
        
        return response
        
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('login')
    except ImportError:
        messages.error(request, 'PDF generation library not available. Please contact administrator.')
        return redirect('student_dashboard')
    except Exception as e:
        messages.error(request, f'Error generating marksheet: {str(e)}')
        return redirect('student_dashboard')



def get_active_announcements(user_role='all'):
    """Helper function to get active announcements for a specific role"""
    from django.utils import timezone
    from .models import Announcement
    
    now = timezone.now()
    announcements = Announcement.objects.filter(
        is_active=True
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=now)
    ).filter(
        Q(target_audience='all') | Q(target_audience=user_role)
    ).order_by('-priority', '-created_at')[:5]
    
    return announcements



@login_required
def teacher_view_students_history(request):
    """Teacher can view history of students in their classes"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        
        # Get all classes where teacher teaches
        subjects = teacher.subjects.all()
        classes = set([subject.class_assigned for subject in subjects])
        students = Student.objects.filter(student_class__in=classes).select_related('user', 'student_class').order_by('roll_number')
        
        # Get history for these students
        from django.contrib.admin.models import LogEntry
        from django.contrib.contenttypes.models import ContentType
        
        student_content_type = ContentType.objects.get_for_model(Student)
        
        # Get student IDs
        student_ids = [str(s.id) for s in students]
        
        # Get history
        history = LogEntry.objects.filter(
            content_type=student_content_type,
            object_id__in=student_ids
        ).select_related('user').order_by('-action_time')[:50]
        
        # Create a mapping of student data
        student_map = {str(s.id): s for s in students}
        
        context = {
            'teacher': teacher,
            'students': students,
            'history': history,
            'student_map': student_map,
        }
        return render(request, 'students/teacher_view_students_history.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found')
        return redirect('login')


@login_required
def admin_view_all_students_history(request):
    """Admin can view complete history of all students"""
    # Check if user is admin
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            messages.error(request, 'Access denied. Admin only.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            messages.error(request, 'Admin profile not found')
            return redirect('login')
    
    from django.contrib.admin.models import LogEntry
    from django.contrib.contenttypes.models import ContentType
    
    student_content_type = ContentType.objects.get_for_model(Student)
    
    # Get all students
    students = Student.objects.all().select_related('user', 'student_class').order_by('roll_number')
    
    # Filter by student if specified
    student_filter = request.GET.get('student', '')
    if student_filter:
        history = LogEntry.objects.filter(
            content_type=student_content_type,
            object_id=student_filter
        ).select_related('user').order_by('-action_time')[:100]
    else:
        # Get recent history for all students
        student_ids = [str(s.id) for s in students]
        history = LogEntry.objects.filter(
            content_type=student_content_type,
            object_id__in=student_ids
        ).select_related('user').order_by('-action_time')[:100]
    
    # Create a mapping of student data
    student_map = {str(s.id): s for s in students}
    
    context = {
        'students': students,
        'history': history,
        'student_map': student_map,
        'student_filter': student_filter,
    }
    return render(request, 'students/admin_view_all_students_history.html', context)


@login_required
def admin_view_all_teachers_history(request):
    """Admin can view complete history of all teachers"""
    # Check if user is admin
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            messages.error(request, 'Access denied. Admin only.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            messages.error(request, 'Admin profile not found')
            return redirect('login')
    
    from django.contrib.admin.models import LogEntry
    from django.contrib.contenttypes.models import ContentType
    
    teacher_content_type = ContentType.objects.get_for_model(Teacher)
    
    # Get all teachers
    teachers = Teacher.objects.all().select_related('user').order_by('employee_id')
    
    # Filter by teacher if specified
    teacher_filter = request.GET.get('teacher', '')
    if teacher_filter:
        history = LogEntry.objects.filter(
            content_type=teacher_content_type,
            object_id=teacher_filter
        ).select_related('user').order_by('-action_time')[:100]
    else:
        # Get recent history for all teachers
        teacher_ids = [str(t.id) for t in teachers]
        history = LogEntry.objects.filter(
            content_type=teacher_content_type,
            object_id__in=teacher_ids
        ).select_related('user').order_by('-action_time')[:100]
    
    # Create a mapping of teacher data
    teacher_map = {str(t.id): t for t in teachers}
    
    context = {
        'teachers': teachers,
        'history': history,
        'teacher_map': teacher_map,
        'teacher_filter': teacher_filter,
    }
    return render(request, 'students/admin_view_all_teachers_history.html', context)



# ==================== ATTENDANCE MANAGEMENT ====================

@login_required
def teacher_mark_attendance(request):
    """Teacher can mark attendance for their classes"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        
        # Get teacher's subjects and classes
        subjects = teacher.subjects.all()
        classes = set([subject.class_assigned for subject in subjects])
        
        if request.method == 'POST':
            date = request.POST.get('date')
            class_id = request.POST.get('class_id')
            
            if not date or not class_id:
                messages.error(request, 'Date and class are required!')
                return redirect('teacher_mark_attendance')
            
            selected_class = get_object_or_404(Class, id=class_id)
            students = Student.objects.filter(student_class=selected_class).order_by('roll_number')
            
            # Process attendance for each student
            from .models import Attendance
            from django.utils import timezone
            
            for student in students:
                status = request.POST.get(f'status_{student.id}')
                remarks = request.POST.get(f'remarks_{student.id}', '')
                
                if status:
                    Attendance.objects.update_or_create(
                        student=student,
                        date=date,
                        defaults={
                            'status': status,
                            'marked_by': request.user,
                            'remarks': remarks
                        }
                    )
            
            messages.success(request, f'Attendance marked successfully for {selected_class.name} on {date}')
            return redirect('teacher_mark_attendance')
        
        context = {
            'teacher': teacher,
            'classes': classes,
        }
        return render(request, 'students/teacher_mark_attendance.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found')
        return redirect('login')


@login_required
def teacher_view_attendance(request):
    """Teacher can view attendance records for their classes"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        from .models import Attendance
        
        # Get teacher's subjects and classes
        subjects = teacher.subjects.all()
        classes = set([subject.class_assigned for subject in subjects])
        student_ids = Student.objects.filter(student_class__in=classes).values_list('id', flat=True)
        
        # Get attendance records
        attendance_records = Attendance.objects.filter(
            student_id__in=student_ids
        ).select_related('student__user', 'student__student_class', 'marked_by').order_by('-date', 'student__roll_number')
        
        # Filter by date range if provided
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        class_filter = request.GET.get('class_id')
        
        if start_date:
            attendance_records = attendance_records.filter(date__gte=start_date)
        if end_date:
            attendance_records = attendance_records.filter(date__lte=end_date)
        if class_filter:
            attendance_records = attendance_records.filter(student__student_class_id=class_filter)
        
        context = {
            'teacher': teacher,
            'attendance_records': attendance_records[:100],
            'classes': classes,
            'start_date': start_date,
            'end_date': end_date,
            'class_filter': class_filter,
        }
        return render(request, 'students/teacher_view_attendance.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found')
        return redirect('login')


@login_required
def student_view_attendance(request):
    """Student can view their own attendance records"""
    try:
        student = Student.objects.get(user=request.user)
        from .models import Attendance
        
        # Get student's attendance records
        attendance_records = Attendance.objects.filter(
            student=student
        ).select_related('marked_by').order_by('-date')
        
        # Calculate statistics
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status='present').count()
        absent_days = attendance_records.filter(status='absent').count()
        late_days = attendance_records.filter(status='late').count()
        
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
        
        context = {
            'student': student,
            'attendance_records': attendance_records[:50],
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'attendance_percentage': round(attendance_percentage, 2),
        }
        return render(request, 'students/student_view_attendance.html', context)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('login')


# ==================== ASSIGNMENT MANAGEMENT ====================

@login_required
def teacher_create_assignment(request):
    """Teacher can create assignments for their classes"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        from .models import Assignment
        
        if request.method == 'POST':
            title = request.POST.get('title')
            description = request.POST.get('description')
            subject_id = request.POST.get('subject_id')
            class_id = request.POST.get('class_id')
            max_marks = request.POST.get('max_marks')
            due_date = request.POST.get('due_date')
            attachment = request.FILES.get('attachment')
            
            if not all([title, description, subject_id, class_id, max_marks, due_date]):
                messages.error(request, 'All fields are required!')
                return redirect('teacher_create_assignment')
            
            subject = get_object_or_404(Subject, id=subject_id)
            class_obj = get_object_or_404(Class, id=class_id)
            
            # Verify teacher teaches this subject
            if subject not in teacher.subjects.all():
                messages.error(request, 'You are not authorized to create assignments for this subject!')
                return redirect('teacher_create_assignment')
            
            assignment = Assignment.objects.create(
                title=title,
                description=description,
                subject=subject,
                class_assigned=class_obj,
                created_by=request.user,
                max_marks=max_marks,
                due_date=due_date,
                status='published',
                attachment=attachment
            )
            
            messages.success(request, f'Assignment "{title}" created successfully!')
            return redirect('teacher_view_assignments')
        
        # Get teacher's subjects
        subjects = teacher.subjects.all()
        classes = set([subject.class_assigned for subject in subjects])
        
        context = {
            'teacher': teacher,
            'subjects': subjects,
            'classes': classes,
        }
        return render(request, 'students/teacher_create_assignment.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found')
        return redirect('login')


@login_required
def teacher_view_assignments(request):
    """Teacher can view all their assignments"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        from .models import Assignment
        
        # Get assignments created by this teacher
        assignments = Assignment.objects.filter(
            created_by=request.user
        ).select_related('subject', 'class_assigned').order_by('-created_at')
        
        context = {
            'teacher': teacher,
            'assignments': assignments,
        }
        return render(request, 'students/teacher_view_assignments.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found')
        return redirect('login')


@login_required
def teacher_assignment_detail(request, assignment_id):
    """Teacher can view assignment details and submissions"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        from .models import Assignment, AssignmentSubmission
        
        assignment = get_object_or_404(Assignment, id=assignment_id, created_by=request.user)
        submissions = AssignmentSubmission.objects.filter(
            assignment=assignment
        ).select_related('student__user').order_by('-submitted_at')
        
        # Calculate statistics
        total_students = Student.objects.filter(student_class=assignment.class_assigned).count()
        submitted_count = submissions.count()
        graded_count = submissions.filter(status='graded').count()
        pending_count = submitted_count - graded_count
        
        context = {
            'teacher': teacher,
            'assignment': assignment,
            'submissions': submissions,
            'total_students': total_students,
            'submitted_count': submitted_count,
            'graded_count': graded_count,
            'pending_count': pending_count,
        }
        return render(request, 'students/teacher_assignment_detail.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found')
        return redirect('login')


@login_required
def teacher_grade_submission(request, submission_id):
    """Teacher can grade a student's assignment submission"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        from .models import AssignmentSubmission
        from django.utils import timezone
        
        submission = get_object_or_404(AssignmentSubmission, id=submission_id)
        
        # Verify teacher created this assignment
        if submission.assignment.created_by != request.user:
            messages.error(request, 'You are not authorized to grade this submission!')
            return redirect('teacher_view_assignments')
        
        if request.method == 'POST':
            marks = request.POST.get('marks')
            feedback = request.POST.get('feedback', '')
            
            if not marks:
                messages.error(request, 'Marks are required!')
                return redirect('teacher_grade_submission', submission_id=submission_id)
            
            try:
                marks = int(marks)
                if marks < 0 or marks > submission.assignment.max_marks:
                    messages.error(request, f'Marks must be between 0 and {submission.assignment.max_marks}!')
                    return redirect('teacher_grade_submission', submission_id=submission_id)
            except ValueError:
                messages.error(request, 'Invalid marks value!')
                return redirect('teacher_grade_submission', submission_id=submission_id)
            
            submission.marks_obtained = marks
            submission.feedback = feedback
            submission.status = 'graded'
            submission.graded_by = request.user
            submission.graded_at = timezone.now()
            submission.save()
            
            messages.success(request, f'Submission graded successfully! Marks: {marks}/{submission.assignment.max_marks}')
            return redirect('teacher_assignment_detail', assignment_id=submission.assignment.id)
        
        context = {
            'teacher': teacher,
            'submission': submission,
        }
        return render(request, 'students/teacher_grade_submission.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found')
        return redirect('login')


@login_required
def student_view_assignments(request):
    """Student can view assignments for their class"""
    try:
        student = Student.objects.get(user=request.user)
        from .models import Assignment, AssignmentSubmission
        
        # Get assignments for student's class
        assignments = Assignment.objects.filter(
            class_assigned=student.student_class,
            status='published'
        ).select_related('subject', 'created_by').order_by('-due_date')
        
        # Get student's submissions
        submissions = AssignmentSubmission.objects.filter(
            student=student
        ).values_list('assignment_id', flat=True)
        
        # Mark which assignments have been submitted
        for assignment in assignments:
            assignment.is_submitted = assignment.id in submissions
        
        context = {
            'student': student,
            'assignments': assignments,
        }
        return render(request, 'students/student_view_assignments.html', context)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('login')


@login_required
def student_assignment_detail(request, assignment_id):
    """Student can view assignment details and submit"""
    try:
        student = Student.objects.get(user=request.user)
        from .models import Assignment, AssignmentSubmission
        
        assignment = get_object_or_404(Assignment, id=assignment_id, class_assigned=student.student_class)
        
        # Check if already submitted
        try:
            submission = AssignmentSubmission.objects.get(assignment=assignment, student=student)
        except AssignmentSubmission.DoesNotExist:
            submission = None
        
        context = {
            'student': student,
            'assignment': assignment,
            'submission': submission,
        }
        return render(request, 'students/student_assignment_detail.html', context)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('login')


@login_required
def student_submit_assignment(request, assignment_id):
    """Student can submit an assignment"""
    try:
        student = Student.objects.get(user=request.user)
        from .models import Assignment, AssignmentSubmission
        from django.utils import timezone
        
        assignment = get_object_or_404(Assignment, id=assignment_id, class_assigned=student.student_class)
        
        # Check if already submitted
        if AssignmentSubmission.objects.filter(assignment=assignment, student=student).exists():
            messages.error(request, 'You have already submitted this assignment!')
            return redirect('student_assignment_detail', assignment_id=assignment_id)
        
        if request.method == 'POST':
            submission_file = request.FILES.get('submission_file')
            submission_text = request.POST.get('submission_text', '')
            
            if not submission_file and not submission_text:
                messages.error(request, 'Please provide either a file or text submission!')
                return redirect('student_submit_assignment', assignment_id=assignment_id)
            
            # Determine if submission is late
            now = timezone.now()
            status = 'late' if now > assignment.due_date else 'submitted'
            
            submission = AssignmentSubmission.objects.create(
                assignment=assignment,
                student=student,
                submission_file=submission_file,
                submission_text=submission_text,
                status=status
            )
            
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('student_assignment_detail', assignment_id=assignment_id)
        
        context = {
            'student': student,
            'assignment': assignment,
        }
        return render(request, 'students/student_submit_assignment.html', context)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('login')



# ==================== ADMIN LOGIN HISTORY ====================

@login_required
def admin_view_login_history(request):
    """Admin can view login history of all users"""
    # Check if user is admin
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            messages.error(request, 'Access denied. Admin only.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            messages.error(request, 'Admin profile not found')
            return redirect('login')
    
    from django.contrib.admin.models import LogEntry
    from django.contrib.contenttypes.models import ContentType
    from datetime import datetime, timedelta
    from django.db.models import Count
    
    # Get all log entries with optimized query
    all_history = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')
    
    # Filter options
    user_filter = request.GET.get('user', '')
    action_filter = request.GET.get('action', '')
    date_filter = request.GET.get('date', '')
    role_filter = request.GET.get('role', '')
    content_type_filter = request.GET.get('content_type', '')
    
    # Apply filters
    history = all_history
    
    if user_filter:
        history = history.filter(user__username__icontains=user_filter)
    
    if action_filter:
        history = history.filter(action_flag=action_filter)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d')
            next_day = filter_date + timedelta(days=1)
            history = history.filter(action_time__gte=filter_date, action_time__lt=next_day)
        except ValueError:
            messages.warning(request, 'Invalid date format')
    
    if content_type_filter:
        history = history.filter(content_type__model=content_type_filter)
    
    # Get user profiles for role information
    user_profiles = {}
    for up in UserProfile.objects.all().select_related('user'):
        user_profiles[up.user.id] = up.role
    
    # Filter by role if specified
    if role_filter:
        role_user_ids = [uid for uid, role in user_profiles.items() if role == role_filter]
        history = history.filter(user_id__in=role_user_ids)
    
    # Get statistics
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    total_actions = all_history.count()
    today_actions = all_history.filter(action_time__date=today).count()
    week_actions = all_history.filter(action_time__date__gte=week_ago).count()
    month_actions = all_history.filter(action_time__date__gte=month_ago).count()
    
    # Action type breakdown
    additions = all_history.filter(action_flag=1).count()
    changes = all_history.filter(action_flag=2).count()
    deletions = all_history.filter(action_flag=3).count()
    
    # Most active users (top 5)
    most_active_users = all_history.values('user__username').annotate(
        action_count=Count('id')
    ).order_by('-action_count')[:5]
    
    # Most modified content types
    top_content_types = all_history.values('content_type__model').annotate(
        action_count=Count('id')
    ).order_by('-action_count')[:5]
    
    # Get all users for filter dropdown
    all_users = User.objects.all().order_by('username')
    
    # Get unique content types for filter
    content_types = ContentType.objects.filter(
        id__in=all_history.values_list('content_type_id', flat=True).distinct()
    ).order_by('model')
    
    # Limit history to 100 records for display
    history_display = history[:100]
    filtered_count = history.count()
    
    context = {
        'history': history_display,
        'all_users': all_users,
        'content_types': content_types,
        'user_filter': user_filter,
        'action_filter': action_filter,
        'date_filter': date_filter,
        'role_filter': role_filter,
        'content_type_filter': content_type_filter,
        'total_actions': total_actions,
        'today_actions': today_actions,
        'week_actions': week_actions,
        'month_actions': month_actions,
        'additions': additions,
        'changes': changes,
        'deletions': deletions,
        'filtered_count': filtered_count,
        'user_profiles': user_profiles,
        'most_active_users': most_active_users,
        'top_content_types': top_content_types,
    }
    return render(request, 'students/admin_view_login_history.html', context)


@login_required
def admin_view_admin_history(request):
    """Admin can view their own login and activity history"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            messages.error(request, 'Access denied. Admin only.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            messages.error(request, 'Admin profile not found')
            return redirect('login')
    
    from django.contrib.admin.models import LogEntry
    
    # Get current admin's activity history
    history = LogEntry.objects.filter(
        user=request.user
    ).select_related('content_type').order_by('-action_time')[:100]
    
    # Calculate statistics
    from datetime import datetime, timedelta
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    total_actions = LogEntry.objects.filter(user=request.user).count()
    today_actions = LogEntry.objects.filter(user=request.user, action_time__date=today).count()
    week_actions = LogEntry.objects.filter(user=request.user, action_time__date__gte=week_ago).count()
    
    # Get action type breakdown
    additions = LogEntry.objects.filter(user=request.user, action_flag=1).count()
    changes = LogEntry.objects.filter(user=request.user, action_flag=2).count()
    deletions = LogEntry.objects.filter(user=request.user, action_flag=3).count()
    
    context = {
        'history': history,
        'total_actions': total_actions,
        'today_actions': today_actions,
        'week_actions': week_actions,
        'additions': additions,
        'changes': changes,
        'deletions': deletions,
    }
    return render(request, 'students/admin_view_admin_history.html', context)

