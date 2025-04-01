from django.contrib import admin
from .models import Analytics, UserActivity, DashboardNotification

class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_students', 'total_consultants', 'total_applications', 
                    'applications_accepted', 'applications_rejected', 'applications_processing')
    readonly_fields = ('date',)
    date_hierarchy = 'date'

class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'ip_address', 'timestamp')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__username', 'user__email', 'description')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)

class DashboardNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username', 'user__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

admin.site.register(Analytics, AnalyticsAdmin)
admin.site.register(UserActivity, UserActivityAdmin)
admin.site.register(DashboardNotification, DashboardNotificationAdmin)
