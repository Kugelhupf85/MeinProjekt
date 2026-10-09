"""
Django Admin configuration for Permissions App.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models.permission import Permission
from .logging import PermissionLog


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    Admin interface for Permission model.
    """
    
    list_display = [
        'user_email',
        'permission_type',
        'resource_type',
        'resource_link',
        'is_active',
        'granted_at',
        'granted_by_email',
        'is_expired_display',
    ]
    
    list_filter = [
        'permission_type',
        'resource_type',
        'is_active',
        'granted_at',
        'expires_at',
    ]
    
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'granted_by__email',
        'notes',
    ]
    
    readonly_fields = [
        'granted_at',
        'resource_type',
        'content_type',
        'object_id',
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'granted_by')
        }),
        ('Permission Details', {
            'fields': ('permission_type', 'resource_type', 'content_type', 'object_id')
        }),
        ('Status', {
            'fields': ('is_active', 'expires_at', 'granted_at')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'activate_permissions',
        'deactivate_permissions',
        'extend_expiration',
    ]
    
    def user_email(self, obj):
        """Display user email."""
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def granted_by_email(self, obj):
        """Display granted by email."""
        return obj.granted_by.email if obj.granted_by else '-'
    granted_by_email.short_description = 'Granted By'
    granted_by_email.admin_order_field = 'granted_by__email'
    
    def resource_link(self, obj):
        """Create a link to the resource."""
        try:
            resource = obj.resource
            if resource:
                # Try to get admin URL for the resource
                admin_url = reverse(f'admin:{resource._meta.app_label}_{resource._meta.model_name}_change', args=[resource.id])
                return format_html('<a href="{}">{}</a>', admin_url, str(resource))
            else:
                return f"{obj.resource_type} {obj.object_id}"
        except:
            return f"{obj.resource_type} {obj.object_id}"
    resource_link.short_description = 'Resource'
    
    def is_expired_display(self, obj):
        """Display expiration status."""
        if obj.is_expired():
            return format_html('<span style="color: red;">Expired</span>')
        elif obj.expires_at:
            return format_html('<span style="color: orange;">Expires {}</span>', obj.expires_at.strftime('%Y-%m-%d'))
        else:
            return format_html('<span style="color: green;">No Expiration</span>')
    is_expired_display.short_description = 'Expiration Status'
    
    def activate_permissions(self, request, queryset):
        """Activate selected permissions."""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} permissions activated successfully.')
    activate_permissions.short_description = 'Activate selected permissions'
    
    def deactivate_permissions(self, request, queryset):
        """Deactivate selected permissions."""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} permissions deactivated successfully.')
    deactivate_permissions.short_description = 'Deactivate selected permissions'
    
    def extend_expiration(self, request, queryset):
        """Extend expiration for selected permissions."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Extend by 30 days
        new_expiration = timezone.now() + timedelta(days=30)
        count = queryset.update(expires_at=new_expiration)
        self.message_user(request, f'{count} permissions extended by 30 days.')
    extend_expiration.short_description = 'Extend expiration by 30 days'


@admin.register(PermissionLog)
class PermissionLogAdmin(admin.ModelAdmin):
    """
    Admin interface for PermissionLog model.
    """
    
    list_display = [
        'timestamp',
        'user_email',
        'log_type',
        'resource_type',
        'resource_id',
        'permission_type',
        'success',
        'ip_address',
    ]
    
    list_filter = [
        'log_type',
        'resource_type',
        'permission_type',
        'success',
        'timestamp',
    ]
    
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'ip_address',
        'request_path',
        'notes',
    ]
    
    readonly_fields = [
        'timestamp',
        'user',
        'log_type',
        'resource_type',
        'resource_id',
        'permission_type',
        'success',
        'ip_address',
        'user_agent',
        'request_path',
        'notes',
        'permission',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('timestamp', 'log_type', 'success')
        }),
        ('User Information', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Resource Information', {
            'fields': ('resource_type', 'resource_id', 'permission_type')
        }),
        ('Request Information', {
            'fields': ('request_path',),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'permission'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'export_logs',
        'cleanup_old_logs',
    ]
    
    def user_email(self, obj):
        """Display user email."""
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def has_add_permission(self, request):
        """Disable adding new log entries manually."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing log entries."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion of log entries."""
        return True
    
    def export_logs(self, request, queryset):
        """Export selected logs to CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="permission_logs.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Timestamp', 'User', 'Log Type', 'Resource Type', 'Resource ID',
            'Permission Type', 'Success', 'IP Address', 'Request Path', 'Notes'
        ])
        
        for log in queryset:
            writer.writerow([
                log.timestamp.isoformat(),
                log.user.email,
                log.get_log_type_display(),
                log.resource_type,
                log.resource_id,
                log.permission_type,
                log.success,
                log.ip_address or '',
                log.request_path or '',
                log.notes or '',
            ])
        
        return response
    export_logs.short_description = 'Export selected logs to CSV'
    
    def cleanup_old_logs(self, request, queryset):
        """Clean up old log entries."""
        from .logging import cleanup_old_permission_logs
        
        count = cleanup_old_permission_logs(days=90)
        self.message_user(request, f'{count} old log entries cleaned up.')
    cleanup_old_logs.short_description = 'Clean up old log entries (90+ days)'


# Custom admin site configuration
admin.site.site_header = 'Arcanovi Permissions Administration'
admin.site.site_title = 'Arcanovi Permissions'
admin.site.index_title = 'Permissions Management' 