from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import csv
import datetime
from .models import UserProfile

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


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'role', 'phone', 'created_at', 'view_history_link')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone')
    readonly_fields = ('created_at', 'get_full_history')
    date_hierarchy = 'created_at'
    actions = [export_to_csv, 'export_detailed_profiles']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role')
        }),
        ('Contact Details', {
            'fields': ('phone', 'address')
        }),
        ('History', {
            'fields': ('created_at', 'get_full_history'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'user__first_name'
    
    def view_history_link(self, obj):
        url = reverse('admin:accounts_userprofile_history', args=[obj.pk])
        return format_html('<a href="{}">📜 View History</a>', url)
    view_history_link.short_description = 'History'
    
    def get_full_history(self, obj):
        if obj.pk:
            from django.contrib.admin.models import LogEntry
            history = LogEntry.objects.filter(
                object_id=str(obj.pk),
                content_type__model='userprofile'
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
    
    def export_detailed_profiles(self, request, queryset):
        """Export user profiles with detailed information"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=user_profiles_detailed_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        writer = csv.writer(response)
        writer.writerow(['Username', 'First Name', 'Last Name', 'Email', 'Role', 
                        'Phone', 'Address', 'Date Joined', 'Last Login', 'Is Active'])
        
        for profile in queryset:
            writer.writerow([
                profile.user.username,
                profile.user.first_name,
                profile.user.last_name,
                profile.user.email,
                profile.get_role_display(),
                profile.phone,
                profile.address,
                profile.created_at.strftime('%Y-%m-%d %H:%M'),
                profile.user.last_login.strftime('%Y-%m-%d %H:%M') if profile.user.last_login else 'Never',
                'Yes' if profile.user.is_active else 'No'
            ])
        
        return response
    export_detailed_profiles.short_description = "📥 Export Detailed Profile Data"


admin.site.site_header = "SRMS Administration"
admin.site.site_title = "SRMS Admin Portal"
admin.site.index_title = "Welcome to Student Result Management System"
