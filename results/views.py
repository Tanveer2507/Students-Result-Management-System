from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from students.models import Student, Subject, Class
from .models import Marks, Result

@login_required
def enter_marks(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        subject_id = request.POST.get('subject_id')
        marks_obtained = request.POST.get('marks_obtained')
        exam_date = request.POST.get('exam_date')
        
        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        
        # Check if marks already exist
        marks, created = Marks.objects.update_or_create(
            student=student,
            subject=subject,
            defaults={
                'marks_obtained': marks_obtained,
                'exam_date': exam_date
            }
        )
        
        if created:
            messages.success(request, 'Marks entered successfully')
        else:
            messages.success(request, 'Marks updated successfully')
        
        return redirect('enter_marks')
    
    classes = Class.objects.all()
    subjects = Subject.objects.all()
    students = Student.objects.all().order_by('roll_number')
    
    context = {
        'classes': classes,
        'subjects': subjects,
        'students': students,
    }
    return render(request, 'results/enter_marks.html', context)

@login_required
def generate_result(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    marks_list = Marks.objects.filter(student=student)
    
    if not marks_list.exists():
        messages.error(request, 'No marks found for this student')
        return redirect('student_list')
    
    # Calculate total marks and percentage
    total_obtained = marks_list.aggregate(Sum('marks_obtained'))['marks_obtained__sum']
    total_max = sum([mark.subject.max_marks for mark in marks_list])
    percentage = (total_obtained / total_max) * 100
    
    # Create or update result
    result, created = Result.objects.update_or_create(
        student=student,
        defaults={
            'total_marks': total_obtained,
            'percentage': percentage,
            'published': True
        }
    )
    
    messages.success(request, f'Result generated for {student.user.get_full_name()}')
    return redirect('view_result', student_id=student_id)

@login_required
def view_result(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    marks = Marks.objects.filter(student=student)
    
    try:
        result = Result.objects.get(student=student)
    except Result.DoesNotExist:
        result = None
    
    context = {
        'student': student,
        'marks': marks,
        'result': result,
    }
    return render(request, 'results/view_result.html', context)

@login_required
def all_results(request):
    results = Result.objects.all().select_related('student__user')
    return render(request, 'results/all_results.html', {'results': results})
