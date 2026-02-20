from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import csv
import datetime
from .models import Class, Subject, Student, Teacher, Announcement, Attendance, Assignment, AssignmentSubmission

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


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'get_student_count', 'get_subject_count', 'created_at', 'view_history_link')
    search_fields = ('name', 'section')
    readonly_fields = ('created_at', 'get_full_history')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    actions = [export_to_csv]
    
    fieldsets = (
        ('Class Information', {
            'fields': ('name', 'section')
        }),
        ('Statistics', {
            'fields': ('get_student_count', 'get_subject_count'),
            'classes': ('collapse',)
        }),
        ('History', {
            'fields': ('created_at', 'get_full_history'),
            'classes': ('collapse',)
        }),
    )
    
    def get_student_count(self, obj):
        count = obj.students.count()
        url = reverse('admin:students_student_changelist') + f'?student_class__id__exact={obj.id}'
        return format_html('<a href="{}">{} Students</a>', url, count)
    get_student_count.short_description = 'Total Students'
    
    def get_subject_count(self, obj):
        count = obj.subjects.count()
        url = reverse('admin:students_subject_changelist') + f'?class_assigned__id__exact={obj.id}'
        return format_html('<a href="{}">{} Subjects</a>', url, count)
    get_subject_count.short_description = 'Total Subjects'
    
    def view_history_link(self, obj):
        url = reverse('admin:students_class_history', args=[obj.pk])
        return format_html('<a href="{}">📜 View History</a>', url)
    view_history_link.short_description = 'History'
    
    def get_full_history(self, obj):
        if obj.pk:
            from django.contrib.admin.models import LogEntry
            history = LogEntry.objects.filter(
                object_id=str(obj.pk),
                content_type__model='class'
            ).select_related('user').order_by('-action_time')[:10]
            
            if history:
                html = '<table style="width:100%; border-collapse: collapse;">'
                html += '<tr style="background: #f0f0f0;"><th>Date</th><th>User</th><th>Action</th><th>Changes</th></tr>'
                for entry in history:
                    html += f'<tr><td>{entry.action_time.strftime("%Y-%m-%d %H:%M")}</td>'
                    html += f'<td>{entry.user.username}</td>'
                    html += f'<td>{entry.get_action_flag_display()}</td>'
                    html += f'<td>{entry.get_change_message()}</td></tr>'
                html += '</table>'
                return mark_safe(html)
            return "No history available"
        return "Save the record first to see history"
    get_full_history.short_description = 'Change History'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'class_assigned', 'max_marks', 'pass_marks', 'get_teacher_count', 'view_history_link')
    list_filter = ('class_assigned', 'max_marks', 'pass_marks')
    search_fields = ('name', 'code')
    readonly_fields = ('get_full_history',)
    actions = [export_to_csv]
    
    fieldsets = (
        ('Subject Information', {
            'fields': ('name', 'code', 'class_assigned')
        }),
        ('Marks Configuration', {
            'fields': ('max_marks', 'pass_marks')
        }),
        ('History', {
            'fields': ('get_full_history',),
            'classes': ('collapse',)
        }),
    )
    
    def get_teacher_count(self, obj):
        count = obj.teachers.count()
        return f'{count} Teacher(s)'
    get_teacher_count.short_description = 'Teachers'
    
    def view_history_link(self, obj):
        url = reverse('admin:students_subject_history', args=[obj.pk])
        return format_html('<a href="{}">📜 View History</a>', url)
    view_history_link.short_description = 'History'
    
    def get_full_history(self, obj):
        if obj.pk:
            from django.contrib.admin.models import LogEntry
            history = LogEntry.objects.filter(
                object_id=str(obj.pk),
                content_type__model='subject'
            ).select_related('user').order_by('-action_time')[:10]
            
            if history:
                html = '<table style="width:100%; border-collapse: collapse;">'
                html += '<tr style="background: #f0f0f0;"><th>Date</th><th>User</th><th>Action</th><th>Changes</th></tr>'
                for entry in history:
                    html += f'<tr><td>{entry.action_time.strftime("%Y-%m-%d %H:%M")}</td>'
                    html += f'<td>{entry.user.username}</td>'
                    html += f'<td>{entry.get_action_flag_display()}</td>'
                    html += f'<td>{entry.get_change_message()}</td></tr>'
                html += '</table>'
                return mark_safe(html)
            return "No history available"
        return "Save the record first to see history"
    get_full_history.short_description = 'Change History'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'get_full_name', 'student_class', 'gender', 'phone', 'created_at', 'view_history_link')
    list_filter = ('student_class', 'gender', 'created_at', 'date_of_birth')
    search_fields = ('roll_number', 'user__first_name', 'user__last_name', 'phone', 'father_name', 'mother_name')
    readonly_fields = ('created_at', 'get_full_history', 'get_marks_summary')
    date_hierarchy = 'created_at'
    actions = [export_to_csv, 'export_detailed_csv']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Student Information', {
            'fields': ('roll_number', 'student_class', 'date_of_birth', 'gender', 'profile_picture')
        }),
        ('Family Information', {
            'fields': ('father_name', 'mother_name')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address')
        }),
        ('Academic Summary', {
            'fields': ('get_marks_summary',),
            'classes': ('collapse',)
        }),
        ('History', {
            'fields': ('created_at', 'get_full_history'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'user__first_name'
    
    def get_marks_summary(self, obj):
        from results.models import Marks, Result
        marks = Marks.objects.filter(student=obj)
        
        if marks.exists():
            html = '<table style="width:100%; border-collapse: collapse;">'
            html += '<tr style="background: #f0f0f0;"><th>Subject</th><th>Marks</th><th>Max Marks</th><th>Status</th></tr>'
            for mark in marks:
                status = '✅ Pass' if mark.marks_obtained >= mark.subject.pass_marks else '❌ Fail'
                html += f'<tr><td>{mark.subject.name}</td>'
                html += f'<td>{mark.marks_obtained}</td>'
                html += f'<td>{mark.subject.max_marks}</td>'
                html += f'<td>{status}</td></tr>'
            html += '</table>'
            
            try:
                result = Result.objects.get(student=obj)
                html += f'<br><strong>Total: {result.total_marks} | Percentage: {result.percentage}% | Grade: {result.grade}</strong>'
            except Result.DoesNotExist:
                pass
            
            return mark_safe(html)
        return "No marks available"
    get_marks_summary.short_description = 'Marks Summary'
    
    def view_history_link(self, obj):
        url = reverse('admin:students_student_history', args=[obj.pk])
        return format_html('<a href="{}">📜 View History</a>', url)
    view_history_link.short_description = 'History'
    
    def get_full_history(self, obj):
        if obj.pk:
            from django.contrib.admin.models import LogEntry
            history = LogEntry.objects.filter(
                object_id=str(obj.pk),
                content_type__model='student'
            ).select_related('user').order_by('-action_time')[:15]
            
            if history:
                html = '<table style="width:100%; border-collapse: collapse;">'
                html += '<tr style="background: #f0f0f0;"><th>Date</th><th>User</th><th>Action</th><th>Changes</th></tr>'
                for entry in history:
                    html += f'<tr><td>{entry.action_time.strftime("%Y-%m-%d %H:%M")}</td>'
                    html += f'<td>{entry.user.username}</td>'
                    html += f'<td>{entry.get_action_flag_display()}</td>'
                    html += f'<td>{entry.get_change_message()}</td></tr>'
                html += '</table>'
                return mark_safe(html)
            return "No history available"
        return "Save the record first to see history"
    get_full_history.short_description = 'Change History'
    
    def export_detailed_csv(self, request, queryset):
        """Export students with detailed information"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=students_detailed_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        writer = csv.writer(response)
        writer.writerow(['Roll Number', 'First Name', 'Last Name', 'Class', 'Gender', 'DOB', 
                        'Father Name', 'Mother Name', 'Phone', 'Address', 'Email', 'Created Date'])
        
        for student in queryset:
            writer.writerow([
                student.roll_number,
                student.user.first_name,
                student.user.last_name,
                str(student.student_class),
                student.get_gender_display(),
                student.date_of_birth,
                student.father_name,
                student.mother_name,
                student.phone,
                student.address,
                student.user.email,
                student.created_at.strftime('%Y-%m-%d')
            ])
        
        return response
    export_detailed_csv.short_description = "📥 Export Detailed Student Data"


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'get_full_name', 'phone', 'qualification', 'experience', 'get_subjects', 'created_at', 'view_history_link')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'phone', 'qualification')
    filter_horizontal = ('subjects',)
    readonly_fields = ('created_at', 'get_full_history', 'get_teaching_summary')
    list_filter = ('qualification', 'experience', 'created_at')
    date_hierarchy = 'created_at'
    actions = [export_to_csv, 'export_detailed_csv']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Teacher Information', {
            'fields': ('employee_id', 'email', 'phone', 'qualification', 'specialization', 'experience', 'address', 'profile_picture')
        }),
        ('Assigned Subjects', {
            'fields': ('subjects',)
        }),
        ('Teaching Summary', {
            'fields': ('get_teaching_summary',),
            'classes': ('collapse',)
        }),
        ('History', {
            'fields': ('created_at', 'get_full_history'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'user__first_name'
    
    def get_subjects(self, obj):
        subjects = obj.subjects.all()[:3]
        if subjects:
            return ", ".join([s.name for s in subjects]) + (f" (+{obj.subjects.count() - 3} more)" if obj.subjects.count() > 3 else "")
        return "No subjects assigned"
    get_subjects.short_description = 'Subjects'
    
    def get_teaching_summary(self, obj):
        subjects = obj.subjects.all()
        
        if subjects.exists():
            html = '<table style="width:100%; border-collapse: collapse;">'
            html += '<tr style="background: #f0f0f0;"><th>Subject</th><th>Code</th><th>Class</th><th>Max Marks</th></tr>'
            for subject in subjects:
                html += f'<tr><td>{subject.name}</td>'
                html += f'<td>{subject.code}</td>'
                html += f'<td>{subject.class_assigned}</td>'
                html += f'<td>{subject.max_marks}</td></tr>'
            html += '</table>'
            return mark_safe(html)
        return "No subjects assigned"
    get_teaching_summary.short_description = 'Teaching Summary'
    
    def view_history_link(self, obj):
        url = reverse('admin:students_teacher_history', args=[obj.pk])
        return format_html('<a href="{}">📜 View History</a>', url)
    view_history_link.short_description = 'History'
    
    def get_full_history(self, obj):
        if obj.pk:
            from django.contrib.admin.models import LogEntry
            history = LogEntry.objects.filter(
                object_id=str(obj.pk),
                content_type__model='teacher'
            ).select_related('user').order_by('-action_time')[:15]
            
            if history:
                html = '<table style="width:100%; border-collapse: collapse;">'
                html += '<tr style="background: #f0f0f0;"><th>Date</th><th>User</th><th>Action</th><th>Changes</th></tr>'
                for entry in history:
                    html += f'<tr><td>{entry.action_time.strftime("%Y-%m-%d %H:%M")}</td>'
                    html += f'<td>{entry.user.username}</td>'
                    html += f'<td>{entry.get_action_flag_display()}</td>'
                    html += f'<td>{entry.get_change_message()}</td></tr>'
                html += '</table>'
                return mark_safe(html)
            return "No history available"
        return "Save the record first to see history"
    get_full_history.short_description = 'Change History'
    
    def export_detailed_csv(self, request, queryset):
        """Export teachers with detailed information"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=teachers_detailed_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        writer = csv.writer(response)
        writer.writerow(['Employee ID', 'First Name', 'Last Name', 'Email', 'Phone', 
                        'Qualification', 'Specialization', 'Experience', 'Subjects', 'Created Date'])
        
        for teacher in queryset:
            subjects = ", ".join([s.name for s in teacher.subjects.all()])
            writer.writerow([
                teacher.employee_id,
                teacher.user.first_name,
                teacher.user.last_name,
                teacher.email,
                teacher.phone,
                teacher.qualification,
                teacher.specialization or 'N/A',
                teacher.experience,
                subjects or 'None',
                teacher.created_at.strftime('%Y-%m-%d')
            ])
        
        return response
    export_detailed_csv.short_description = "📥 Export Detailed Teacher Data"



@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_priority_badge', 'target_audience', 'get_status_badge', 'created_by', 'created_at', 'expires_at')
    list_filter = ('priority', 'target_audience', 'is_active', 'created_at')
    search_fields = ('title', 'message')
    readonly_fields = ('created_by', 'created_at', 'get_full_history')
    date_hierarchy = 'created_at'
    actions = [export_to_csv, 'activate_announcements', 'deactivate_announcements']
    
    fieldsets = (
        ('Announcement Details', {
            'fields': ('title', 'message', 'priority', 'target_audience')
        }),
        ('Status & Expiry', {
            'fields': ('is_active', 'expires_at')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
        ('Change History', {
            'fields': ('get_full_history',),
            'classes': ('collapse',)
        }),
    )
    
    def get_priority_badge(self, obj):
        colors = {
            'low': '#17a2b8',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'urgent': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.priority, '#6c757d'),
            obj.get_priority_display()
        )
    get_priority_badge.short_description = 'Priority'
    
    def get_status_badge(self, obj):
        if not obj.is_active:
            return format_html('<span style="color: #6c757d;">⚫ Inactive</span>')
        elif obj.is_expired():
            return format_html('<span style="color: #dc3545;">⏰ Expired</span>')
        else:
            return format_html('<span style="color: #28a745;">✅ Active</span>')
    get_status_badge.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def activate_announcements(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} announcement(s) activated successfully.')
    activate_announcements.short_description = '✅ Activate Selected Announcements'
    
    def deactivate_announcements(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} announcement(s) deactivated successfully.')
    deactivate_announcements.short_description = '⛔ Deactivate Selected Announcements'
    
    def get_full_history(self, obj):
        from django.contrib.admin.models import LogEntry
        if obj.pk:
            history = LogEntry.objects.filter(
                object_id=str(obj.pk),
                content_type__model='announcement'
            ).select_related('user').order_by('-action_time')[:15]
            
            if history:
                html = '<div style="max-height: 400px; overflow-y: auto;">'
                html += '<table style="width: 100%; border-collapse: collapse;">'
                html += '<tr style="background-color: #f8f9fa;"><th style="padding: 8px; border: 1px solid #dee2e6;">Date</th><th style="padding: 8px; border: 1px solid #dee2e6;">User</th><th style="padding: 8px; border: 1px solid #dee2e6;">Action</th><th style="padding: 8px; border: 1px solid #dee2e6;">Changes</th></tr>'
                
                for entry in history:
                    action_map = {1: 'Added', 2: 'Changed', 3: 'Deleted'}
                    action = action_map.get(entry.action_flag, 'Unknown')
                    html += f'<tr><td style="padding: 8px; border: 1px solid #dee2e6;">{entry.action_time.strftime("%Y-%m-%d %H:%M:%S")}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #dee2e6;">{entry.user.username}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #dee2e6;">{action}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #dee2e6;">{entry.change_message}</td></tr>'
                
                html += '</table></div>'
                return mark_safe(html)
            return "No history available"
        return "Save the record first to see history"
    get_full_history.short_description = 'Complete Change History'



@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'get_status_badge', 'marked_by', 'created_at')
    list_filter = ('status', 'date', 'student__student_class')
    search_fields = ('student__roll_number', 'student__user__first_name', 'student__user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'get_full_history')
    date_hierarchy = 'date'
    actions = [export_to_csv, 'mark_present', 'mark_absent']
    
    fieldsets = (
        ('Attendance Information', {
            'fields': ('student', 'date', 'status', 'marked_by', 'remarks')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Change History', {
            'fields': ('get_full_history',),
            'classes': ('collapse',)
        }),
    )
    
    def get_status_badge(self, obj):
        colors = {
            'present': '#28a745',
            'absent': '#dc3545',
            'late': '#ffc107',
            'excused': '#17a2b8'
        }
        icons = {
            'present': '✅',
            'absent': '❌',
            'late': '⏰',
            'excused': '📝'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            colors.get(obj.status, '#6c757d'),
            icons.get(obj.status, ''),
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.marked_by = request.user
        super().save_model(request, obj, form, change)
    
    def mark_present(self, request, queryset):
        updated = queryset.update(status='present')
        self.message_user(request, f'{updated} attendance record(s) marked as Present.')
    mark_present.short_description = '✅ Mark Selected as Present'
    
    def mark_absent(self, request, queryset):
        updated = queryset.update(status='absent')
        self.message_user(request, f'{updated} attendance record(s) marked as Absent.')
    mark_absent.short_description = '❌ Mark Selected as Absent'
    
    def get_full_history(self, obj):
        from django.contrib.admin.models import LogEntry
        if obj.pk:
            history = LogEntry.objects.filter(
                object_id=str(obj.pk),
                content_type__model='attendance'
            ).select_related('user').order_by('-action_time')[:15]
            
            if history:
                html = '<div style="max-height: 400px; overflow-y: auto;">'
                html += '<table style="width: 100%; border-collapse: collapse;">'
                html += '<tr style="background-color: #f8f9fa;"><th style="padding: 8px; border: 1px solid #dee2e6;">Date</th><th style="padding: 8px; border: 1px solid #dee2e6;">User</th><th style="padding: 8px; border: 1px solid #dee2e6;">Action</th><th style="padding: 8px; border: 1px solid #dee2e6;">Changes</th></tr>'
                
                for entry in history:
                    action_map = {1: 'Added', 2: 'Changed', 3: 'Deleted'}
                    action = action_map.get(entry.action_flag, 'Unknown')
                    html += f'<tr><td style="padding: 8px; border: 1px solid #dee2e6;">{entry.action_time.strftime("%Y-%m-%d %H:%M:%S")}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #dee2e6;">{entry.user.username}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #dee2e6;">{action}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #dee2e6;">{entry.change_message}</td></tr>'
                
                html += '</table></div>'
                return mark_safe(html)
            return "No history available"
        return "Save the record first to see history"
    get_full_history.short_description = 'Complete Change History'


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'class_assigned', 'get_status_badge', 'due_date', 'max_marks', 'get_submission_count', 'created_by')
    list_filter = ('status', 'subject', 'class_assigned', 'due_date')
    search_fields = ('title', 'description', 'subject__name')
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'get_full_history')
    date_hierarchy = 'due_date'
    actions = [export_to_csv, 'publish_assignments', 'close_assignments']
    
    fieldsets = (
        ('Assignment Details', {
            'fields': ('title', 'description', 'subject', 'class_assigned', 'max_marks')
        }),
        ('Schedule & Status', {
            'fields': ('due_date', 'status', 'attachment')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Change History', {
            'fields': ('get_full_history',),
            'classes': ('collapse',)
        }),
    )
    
    def get_status_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'published': '#28a745',
            'closed': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    
    def get_submission_count(self, obj):
        count = obj.submissions.count()
        total_students = Student.objects.filter(student_class=obj.class_assigned).count()
        percentage = (count / total_students * 100) if total_students > 0 else 0
        return format_html(
            '<span style="font-weight: bold;">{}/{}</span> <span style="color: #6c757d;">({:.1f}%)</span>',
            count, total_students, percentage
        )
    get_submission_count.short_description = 'Submissions'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def publish_assignments(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} assignment(s) published successfully.')
    publish_assignments.short_description = '📢 Publish Selected Assignments'
    
    def close_assignments(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f'{updated} assignment(s) closed successfully.')
    close_assignments.short_description = '🔒 Close Selected Assignments'
    
    def get_full_history(self, obj):
        from django.contrib.admin.models import LogEntry
        if obj.pk:
            history = LogEntry.objects.filter(
                object_id=str(obj.pk),
                content_type__model='assignment'
            ).select_related('user').order_by('-action_time')[:15]
            
            if history:
                html = '<div style="max-height: 400px; overflow-y: auto;">'
                html += '<table style="width: 100%; border-collapse: collapse;">'
                html += '<tr style="background-color: #f8f9fa;"><th style="padding: 8px; border: 1px solid #dee2e6;">Date</th><th style="padding: 8px; border: 1px solid #dee2e6;">User</th><th style="padding: 8px; border: 1px solid #dee2e6;">Action</th><th style="padding: 8px; border: 1px solid #dee2e6;">Changes</th></tr>'
                
                for entry in history:
                    action_map = {1: 'Added', 2: 'Changed', 3: 'Deleted'}
                    action = action_map.get(entry.action_flag, 'Unknown')
                    html += f'<tr><td style="padding: 8px; border: 1px solid #dee2e6;">{entry.action_time.strftime("%Y-%m-%d %H:%M:%S")}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #dee2e6;">{entry.user.username}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #dee2e6;">{action}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #dee2e6;">{entry.change_message}</td></tr>'
                
                html += '</table></div>'
                return mark_safe(html)
            return "No history available"
        return "Save the record first to see history"
    get_full_history.short_description = 'Complete Change History'


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'get_status_badge', 'marks_obtained', 'submitted_at', 'get_late_badge', 'graded_by')
    list_filter = ('status', 'assignment__subject', 'assignment__class_assigned', 'submitted_at')
    search_fields = ('student__roll_number', 'student__user__first_name', 'assignment__title')
    readonly_fields = ('submitted_at', 'graded_at', 'get_full_history')
    date_hierarchy = 'submitted_at'
    actions = [export_to_csv, 'mark_as_graded']
    
    fieldsets = (
        ('Submission Details', {
            'fields': ('assignment', 'student', 'submission_file', 'submission_text')
        }),
        ('Grading', {
            'fields': ('status', 'marks_obtained', 'feedback', 'graded_by', 'graded_at')
        }),
        ('Timestamps', {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        }),
        ('Change History', {
            'fields': ('get_full_history',),
            'classes': ('collapse',)
        }),
    )
    
    def get_status_badge(self, obj):
        colors = {
            'submitted': '#17a2b8',
            'late': '#ffc107',
            'graded': '#28a745'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    
    def get_late_badge(self, obj):
        if obj.is_late():
            return format_html('<span style="color: #dc3545; font-weight: bold;">⏰ Late</span>')
        return format_html('<span style="color: #28a745;">✅ On Time</span>')
    get_late_badge.short_description = 'Timeliness'
    
    def save_model(self, request, obj, form, change):
        if obj.status == 'graded' and not obj.graded_by:
            obj.graded_by = request.user
            from django.utils import timezone
            obj.graded_at = timezone.now()
        super().save_model(request, obj, form, change)
    
    def mark_as_graded(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='graded', graded_by=request.user, graded_at=timezone.now())
        self.message_user(request, f'{updated} submission(s) marked as graded.')
    mark_as_graded.short_description = '✅ Mark Selected as Graded'
    
    def get_full_history(self, obj):
        from django.contrib.admin.models import LogEntry
        if obj.pk:
            history = LogEntry.objects.filter(
                object_id=str(obj.pk),
                content_type__model='assignmentsubmission'
            ).select_related('user').order_by('-action_time')[:15]
            
            if history:
                html = '<div style="max-height: 400px; overflow-y: auto;">'
                html += '<table style="width: 100%; border-collapse: collapse;">'
                html += '<tr style="background-color: #f8f9fa;"><th style="padding: 8px; border: 1px solid #dee2e6;">Date</th><th style="padding: 8px; border: 1px solid #dee2e6;">User</th><th style="padding: 8px; border: 1px solid #dee2e6;">Action</th><th style="padding: 8px; border: 1px solid #dee2e6;">Changes</th></tr>'
                

                for entry in history:
                    action_colors = {1: '#28a745', 2: '#ffc107', 3: '#dc3545'}
                    action_names = {1: 'Added', 2: 'Changed', 3: 'Deleted'}
                    html += f'<tr><td style="padding: 8px; border: 1px solid #dee2e6;">{entry.action_time.strftime("%Y-%m-%d %H:%M")}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #dee2e6;">{entry.user.username}</td>'
                    html += f'<td style="padding: 8px; border: 1px solid #dee2e6;"><span style="color: {action_colors.get(entry.action_flag, "#6c757d")}; font-weight: bold;">{action_names.get(entry.action_flag, "Unknown")}</span></td>'
                    html += f'<td style="padding: 8px; border: 1px solid #dee2e6;">{entry.change_message or "No details"}</td></tr>'
                
                html += '</table></div>'
                return mark_safe(html)
            return "No history available"
        return "Save the record first to see history"
    get_full_history.short_description = 'Complete Change History'
