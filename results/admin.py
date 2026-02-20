from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import csv
import datetime
from .models import Marks, Result

# Custom Admin Actions for Export
def export_to_csv(modeladmin, request, queryset):
    """Export selected records to CSV"""
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={opts.verbose_name_plural}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    
    # Write headers
    writer.writerow([field.verbose_name for field in fields])
    
    # Write data
    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field.name)
            if callable(value):
                value = value()
            row.append(str(value))
        writer.writerow(row)
    
    return response
export_to_csv.short_description = "📥 Export Selected to CSV"


@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'get_roll_number', 'subject', 'marks_obtained', 'get_max_marks', 'exam_date', 'get_status', 'updated_at', 'view_history_link')
    list_filter = ('subject', 'exam_date', 'created_at', 'updated_at')
    search_fields = ('student__roll_number', 'student__user__first_name', 'student__user__last_name', 'subject__name')
    readonly_fields = ('created_at', 'updated_at', 'get_full_history')
    date_hierarchy = 'exam_date'
    actions = [export_to_csv, 'export_detailed_marks']
    
    fieldsets = (
        ('Student & Subject', {
            'fields': ('student', 'subject')
        }),
        ('Marks Information', {
            'fields': ('marks_obtained', 'exam_date')
        }),
        ('History', {
            'fields': ('created_at', 'updated_at', 'get_full_history'),
            'classes': ('collapse',)
        }),
    )
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    get_student_name.short_description = 'Student Name'
    get_student_name.admin_order_field = 'student__user__first_name'
    
    def get_roll_number(self, obj):
        return obj.student.roll_number
    get_roll_number.short_description = 'Roll Number'
    get_roll_number.admin_order_field = 'student__roll_number'
    
    def get_max_marks(self, obj):
        return obj.subject.max_marks
    get_max_marks.short_description = 'Max Marks'
    
    def get_status(self, obj):
        if obj.marks_obtained >= obj.subject.pass_marks:
            return format_html('<span style="color: green; font-weight: bold;">✅ Pass</span>')
        return format_html('<span style="color: red; font-weight: bold;">❌ Fail</span>')
    get_status.short_description = 'Status'
    
    def view_history_link(self, obj):
        url = reverse('admin:results_marks_history', args=[obj.pk])
        return format_html('<a href="{}">📜 View History</a>', url)
    view_history_link.short_description = 'History'
    
    def get_full_history(self, obj):
        if obj.pk:
            from django.contrib.admin.models import LogEntry
            history = LogEntry.objects.filter(
                object_id=str(obj.pk),
                content_type__model='marks'
            ).select_related('user').order_by('-action_time')[:15]
            
            if history:
                html = '<table style="width:100%; border-collapse: collapse; border: 1px solid #ddd;">'
                html += '<tr style="background: #f0f0f0;"><th style="padding: 8px; border: 1px solid #ddd;">Date</th><th style="padding: 8px; border: 1px solid #ddd;">User</th><th style="padding: 8px; border: 1px solid #ddd;">Action</th><th style="padding: 8px; border: 1px solid #ddd;">Changes</th></tr>'
                for entry in history:
                    html += f'<tr><td style="padding: 8px; border: 1px solid #ddd;">{entry.action_time.strftime("%Y-%m-%d %H:%M:%S")}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #ddd;">{entry.user.username}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #ddd;">{entry.get_action_flag_display()}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #ddd;">{entry.get_change_message()}</td></tr>'
                html += '</table>'
                return mark_safe(html)
            return "No history available"
        return "Save the record first to see history"
    get_full_history.short_description = 'Complete Change History'
    
    def export_detailed_marks(self, request, queryset):
        """Export marks with detailed information"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=marks_detailed_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        writer = csv.writer(response)
        writer.writerow(['Roll Number', 'Student Name', 'Class', 'Subject', 'Subject Code', 
                        'Marks Obtained', 'Max Marks', 'Pass Marks', 'Percentage', 'Status', 
                        'Exam Date', 'Created Date', 'Last Updated'])
        
        for mark in queryset:
            percentage = (mark.marks_obtained / mark.subject.max_marks) * 100
            status = 'Pass' if mark.marks_obtained >= mark.subject.pass_marks else 'Fail'
            
            writer.writerow([
                mark.student.roll_number,
                mark.student.user.get_full_name(),
                str(mark.student.student_class),
                mark.subject.name,
                mark.subject.code,
                mark.marks_obtained,
                mark.subject.max_marks,
                mark.subject.pass_marks,
                f'{percentage:.2f}%',
                status,
                mark.exam_date,
                mark.created_at.strftime('%Y-%m-%d %H:%M'),
                mark.updated_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
    export_detailed_marks.short_description = "📥 Export Detailed Marks Data"


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'get_roll_number', 'get_class', 'total_marks', 'percentage', 'grade', 'status', 'published', 'updated_at', 'view_history_link')
    list_filter = ('grade', 'status', 'published', 'created_at', 'updated_at')
    search_fields = ('student__roll_number', 'student__user__first_name', 'student__user__last_name')
    list_editable = ('published',)
    readonly_fields = ('grade', 'status', 'created_at', 'updated_at', 'get_full_history', 'get_subject_wise_marks')
    date_hierarchy = 'created_at'
    actions = [export_to_csv, 'publish_results', 'unpublish_results', 'export_detailed_results']
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student',)
        }),
        ('Result Details', {
            'fields': ('total_marks', 'percentage', 'grade', 'status')
        }),
        ('Subject-wise Marks', {
            'fields': ('get_subject_wise_marks',),
            'classes': ('collapse',)
        }),
        ('Publication', {
            'fields': ('published',)
        }),
        ('History', {
            'fields': ('created_at', 'updated_at', 'get_full_history'),
            'classes': ('collapse',)
        }),
    )
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    get_student_name.short_description = 'Student Name'
    get_student_name.admin_order_field = 'student__user__first_name'
    
    def get_roll_number(self, obj):
        return obj.student.roll_number
    get_roll_number.short_description = 'Roll Number'
    get_roll_number.admin_order_field = 'student__roll_number'
    
    def get_class(self, obj):
        return obj.student.student_class
    get_class.short_description = 'Class'
    
    def get_subject_wise_marks(self, obj):
        marks = obj.student.marks.all()
        
        if marks.exists():
            html = '<table style="width:100%; border-collapse: collapse; border: 1px solid #ddd;">'
            html += '<tr style="background: #f0f0f0;"><th style="padding: 8px; border: 1px solid #ddd;">Subject</th><th style="padding: 8px; border: 1px solid #ddd;">Marks Obtained</th><th style="padding: 8px; border: 1px solid #ddd;">Max Marks</th><th style="padding: 8px; border: 1px solid #ddd;">Percentage</th><th style="padding: 8px; border: 1px solid #ddd;">Status</th></tr>'
            
            for mark in marks:
                percentage = (mark.marks_obtained / mark.subject.max_marks) * 100
                status = '✅ Pass' if mark.marks_obtained >= mark.subject.pass_marks else '❌ Fail'
                
                html += f'<tr><td style="padding: 8px; border: 1px solid #ddd;">{mark.subject.name}</td>'
                html += f'<td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{mark.marks_obtained}</td>'
                html += f'<td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{mark.subject.max_marks}</td>'
                html += f'<td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{percentage:.2f}%</td>'
                html += f'<td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{status}</td></tr>'
            
            html += '</table>'
            return mark_safe(html)
        return "No marks available"
    get_subject_wise_marks.short_description = 'Subject-wise Marks Breakdown'
    
    def view_history_link(self, obj):
        url = reverse('admin:results_result_history', args=[obj.pk])
        return format_html('<a href="{}">📜 View History</a>', url)
    view_history_link.short_description = 'History'
    
    def get_full_history(self, obj):
        if obj.pk:
            from django.contrib.admin.models import LogEntry
            history = LogEntry.objects.filter(
                object_id=str(obj.pk),
                content_type__model='result'
            ).select_related('user').order_by('-action_time')[:15]
            
            if history:
                html = '<table style="width:100%; border-collapse: collapse; border: 1px solid #ddd;">'
                html += '<tr style="background: #f0f0f0;"><th style="padding: 8px; border: 1px solid #ddd;">Date</th><th style="padding: 8px; border: 1px solid #ddd;">User</th><th style="padding: 8px; border: 1px solid #ddd;">Action</th><th style="padding: 8px; border: 1px solid #ddd;">Changes</th></tr>'
                for entry in history:
                    html += f'<tr><td style="padding: 8px; border: 1px solid #ddd;">{entry.action_time.strftime("%Y-%m-%d %H:%M:%S")}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #ddd;">{entry.user.username}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #ddd;">{entry.get_action_flag_display()}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #ddd;">{entry.get_change_message()}</td></tr>'
                html += '</table>'
                return mark_safe(html)
            return "No history available"
        return "Save the record first to see history"
    get_full_history.short_description = 'Complete Change History'
    
    def publish_results(self, request, queryset):
        updated = queryset.update(published=True)
        self.message_user(request, f'{updated} result(s) published successfully.')
    publish_results.short_description = '✅ Publish selected results'
    
    def unpublish_results(self, request, queryset):
        updated = queryset.update(published=False)
        self.message_user(request, f'{updated} result(s) unpublished successfully.')
    unpublish_results.short_description = '❌ Unpublish selected results'
    
    def export_detailed_results(self, request, queryset):
        """Export results with detailed information"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=results_detailed_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        writer = csv.writer(response)
        writer.writerow(['Roll Number', 'Student Name', 'Class', 'Father Name', 'Mother Name',
                        'Total Marks', 'Percentage', 'Grade', 'Status', 'Published', 
                        'Created Date', 'Last Updated'])
        
        for result in queryset:
            writer.writerow([
                result.student.roll_number,
                result.student.user.get_full_name(),
                str(result.student.student_class),
                result.student.father_name,
                result.student.mother_name,
                result.total_marks,
                f'{result.percentage}%',
                result.grade,
                result.status,
                'Yes' if result.published else 'No',
                result.created_at.strftime('%Y-%m-%d %H:%M'),
                result.updated_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
    export_detailed_results.short_description = "📥 Export Detailed Results Data"
