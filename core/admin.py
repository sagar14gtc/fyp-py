from django.contrib import admin
from .models import FAQ, Testimonial, ContactMessage, SiteConfiguration

class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'is_published', 'created_at')
    list_filter = ('category', 'is_published')
    search_fields = ('question', 'answer', 'category')
    list_editable = ('order', 'is_published')

class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'rating', 'is_featured', 'created_at')
    list_filter = ('rating', 'is_featured')
    search_fields = ('name', 'role', 'content')
    list_editable = ('is_featured',)

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    
    def has_add_permission(self, request):
        return False

class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'email', 'phone')
    fieldsets = (
        ('Basic Information', {
            'fields': ('site_name', 'logo', 'favicon', 'email', 'phone', 'address')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'youtube_url')
        }),
        ('Footer', {
            'fields': ('footer_text',)
        }),
    )
    
    def has_add_permission(self, request):
        # Check if an object already exists
        if SiteConfiguration.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(FAQ, FAQAdmin)
admin.site.register(Testimonial, TestimonialAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(SiteConfiguration, SiteConfigurationAdmin)
