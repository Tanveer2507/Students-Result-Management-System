import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'srms_project.settings')
django.setup()

from django.contrib.auth.models import User
from students.models import Student, Class, Subject
from results.models import Marks, Result
from datetime import date

def add_sample_marks():
    """Add sample marks for the demo student"""
    
    try:
        # Get the student
        user = User.objects.get(username='student_demo')
        student = Student.objects.get(user=user)
        student_class = student.student_class
        
        print(f"Adding marks for: {student.user.get_full_name()}")
        print(f"Class: {student_class}")
        print(f"Roll Number: {student.roll_number}\n")
        
        # Create subjects if they don't exist
        subjects_data = [
            {'name': 'Mathematics', 'code': 'MATH101', 'max_marks': 100},
            {'name': 'Science', 'code': 'SCI101', 'max_marks': 100},
            {'name': 'English', 'code': 'ENG101', 'max_marks': 100},
            {'name': 'Social Studies', 'code': 'SS101', 'max_marks': 100},
            {'name': 'Computer Science', 'code': 'CS101', 'max_marks': 100},
        ]
        
        # Sample marks (realistic scores)
        marks_data = [92, 88, 85, 90, 95]
        
        total_marks = 0
        max_total = 0
        
        print("Creating subjects and adding marks:\n")
        
        for i, subject_info in enumerate(subjects_data):
            # Get or create subject
            subject, created = Subject.objects.get_or_create(
                name=subject_info['name'],
                code=subject_info['code'],
                class_assigned=student_class,
                defaults={'max_marks': subject_info['max_marks']}
            )
            
            if created:
                print(f"✅ Created subject: {subject.name}")
            else:
                print(f"✅ Using existing subject: {subject.name}")
            
            # Create or update marks
            marks_obtained = marks_data[i]
            marks, created = Marks.objects.update_or_create(
                student=student,
                subject=subject,
                defaults={
                    'marks_obtained': marks_obtained,
                    'exam_date': date(2026, 2, 1)
                }
            )
            
            percentage = (marks_obtained / subject.max_marks) * 100
            print(f"   Marks: {marks_obtained}/{subject.max_marks} ({percentage:.1f}%)")
            
            total_marks += marks_obtained
            max_total += subject.max_marks
        
        # Calculate overall percentage and grade
        overall_percentage = (total_marks / max_total) * 100
        
        # Determine grade
        if overall_percentage >= 90:
            grade = 'A+'
        elif overall_percentage >= 75:
            grade = 'A'
        elif overall_percentage >= 60:
            grade = 'B'
        elif overall_percentage >= 50:
            grade = 'C'
        elif overall_percentage >= 35:
            grade = 'D'
        else:
            grade = 'F'
        
        # Determine result status
        result_status = 'Pass' if overall_percentage >= 35 else 'Fail'
        
        # Create or update result
        result, created = Result.objects.update_or_create(
            student=student,
            defaults={
                'total_marks': total_marks,
                'percentage': overall_percentage,
                'grade': grade,
                'status': result_status,
                'published': True
            }
        )
        
        print("\n" + "="*60)
        print("🎉 MARKS ADDED SUCCESSFULLY!")
        print("="*60)
        print(f"\n📊 Overall Result:")
        print(f"   Total Marks: {total_marks}/{max_total}")
        print(f"   Percentage: {overall_percentage:.2f}%")
        print(f"   Grade: {grade}")
        print(f"   Status: {result_status}")
        print("\n" + "="*60)
        print("✨ Login to see your marks and result!")
        print("="*60)
        print(f"\n🔗 Login URL: http://127.0.0.1:8000/accounts/login/student/")
        print(f"   Username: student_demo")
        print(f"   Password: demo123")
        
    except User.DoesNotExist:
        print("❌ Error: Student 'student_demo' not found!")
        print("Please run create_test_student_profile.py first")
    except Student.DoesNotExist:
        print("❌ Error: Student profile not found!")
        print("Please run create_test_student_profile.py first")

if __name__ == '__main__':
    add_sample_marks()
