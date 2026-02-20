import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'srms_project.settings')
django.setup()

from students.models import Student, Subject, Class
from results.models import Marks, Result
from datetime import date

def add_marks():
    """Add sample marks for test student"""
    
    print("="*60)
    print("ADDING MARKS FOR TEST STUDENT...")
    print("="*60)
    
    try:
        # Get the test student
        student = Student.objects.get(roll_number='TS001')
        print(f"✅ Found student: {student.user.get_full_name()}")
        
        # Get or create subjects for Class 10 A
        student_class = student.student_class
        
        subjects_data = [
            {'name': 'Mathematics', 'code': 'MATH101', 'max_marks': 100, 'pass_marks': 35},
            {'name': 'Science', 'code': 'SCI101', 'max_marks': 100, 'pass_marks': 35},
            {'name': 'English', 'code': 'ENG101', 'max_marks': 100, 'pass_marks': 35},
            {'name': 'Social Studies', 'code': 'SS101', 'max_marks': 100, 'pass_marks': 35},
            {'name': 'Computer Science', 'code': 'CS101', 'max_marks': 100, 'pass_marks': 35},
        ]
        
        marks_data = [85, 78, 92, 88, 95]  # Sample marks
        
        total_marks = 0
        total_max = 0
        
        for i, subj_data in enumerate(subjects_data):
            # Create or get subject
            subject, created = Subject.objects.get_or_create(
                code=subj_data['code'],
                defaults={
                    'name': subj_data['name'],
                    'class_assigned': student_class,
                    'max_marks': subj_data['max_marks'],
                    'pass_marks': subj_data['pass_marks']
                }
            )
            
            # Create marks
            mark, created = Marks.objects.get_or_create(
                student=student,
                subject=subject,
                defaults={
                    'marks_obtained': marks_data[i],
                    'exam_date': date(2025, 12, 15)
                }
            )
            
            total_marks += marks_data[i]
            total_max += subj_data['max_marks']
            
            print(f"✅ {subject.name}: {marks_data[i]}/{subj_data['max_marks']}")
        
        # Calculate percentage and grade
        percentage = (total_marks / total_max) * 100
        
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
        
        status = 'Pass' if percentage >= 35 else 'Fail'
        
        # Create or update result
        result, created = Result.objects.update_or_create(
            student=student,
            defaults={
                'total_marks': total_marks,
                'percentage': round(percentage, 2),
                'grade': grade,
                'status': status,
                'published': True
            }
        )
        
        print("\n" + "="*60)
        print("🎉 MARKS ADDED SUCCESSFULLY!")
        print("="*60)
        print(f"\n📊 Result Summary:")
        print(f"   Total Marks: {total_marks}/{total_max}")
        print(f"   Percentage: {percentage:.2f}%")
        print(f"   Grade: {grade}")
        print(f"   Status: {status}")
        print("\n" + "="*60)
        print("✨ Student can now view marks and result in dashboard!")
        print("="*60)
        
    except Student.DoesNotExist:
        print("❌ Test student not found. Please create student first.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    add_marks()
