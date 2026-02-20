from django.db import models
from students.models import Student, Subject

class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    exam_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Marks"
        unique_together = ('student', 'subject')
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.subject.name}: {self.marks_obtained}"

class Result(models.Model):
    STATUS_CHOICES = (
        ('Pass', 'Pass'),
        ('Fail', 'Fail'),
    )
    
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='result')
    total_marks = models.DecimalField(max_digits=7, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.grade} ({self.percentage}%)"
    
    def calculate_grade(self):
        """Calculate grade based on percentage"""
        if self.percentage >= 90:
            return 'A+'
        elif self.percentage >= 75:
            return 'A'
        elif self.percentage >= 60:
            return 'B'
        elif self.percentage >= 50:
            return 'C'
        elif self.percentage >= 35:
            return 'D'
        else:
            return 'F'
    
    def save(self, *args, **kwargs):
        self.grade = self.calculate_grade()
        self.status = 'Pass' if self.percentage >= 35 else 'Fail'
        super().save(*args, **kwargs)
