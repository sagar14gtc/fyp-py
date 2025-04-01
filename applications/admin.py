from django.contrib import admin
from .models import Application, Document, ApplicationNote, ApplicationStatus

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1

class ApplicationNoteInline(admin.TabularInline):
    model = ApplicationNote
    extra = 1

class ApplicationStatusInline(admin.TabularInline):
    model = ApplicationStatus
    extra = 0
    readonly_fields = ('status', 'changed_by', 'changed_at')
    can_delete = False

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'student', 'program', 'status', 'application_date', 'consultant', 'last_updated') # Added consultant
    list_filter = ('status', 'application_date', 'program__university__country', 'consultant') # Added country and consultant filters
    search_fields = ('application_id', 'student__email', 'student__username', 'program__name', 'program__university__name') # Added university name
    readonly_fields = ('application_id', 'application_date', 'last_updated') # Added last_updated
    date_hierarchy = 'application_date'
    
    fieldsets = (
        (None, {
            'fields': ('application_id', 'student', 'program', 'consultant', 'status', 'intake_date')
        }),
        ('Student Provided Info', {
            'fields': ('gpa_or_percentage', 'study_gap_years', 'ielts_score', 'duolingo_score'),
        }),
         ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'),
        }),
        ('Timestamps', {
            'fields': ('application_date', 'last_updated'),
        }),
         ('Admin Notes', {
            'fields': ('notes',),
        }),
    )
    
    inlines = [DocumentInline, ApplicationNoteInline, ApplicationStatusInline]

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'application', 'document_type', 'status', 'required', 'upload_date', 'last_updated')
    list_filter = ('document_type', 'status', 'required')
    search_fields = ('name', 'application__application_id', 'application__student__email')
    date_hierarchy = 'upload_date'

admin.site.register(Application, ApplicationAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(ApplicationNote)
admin.site.register(ApplicationStatus)
