from django.contrib import admin
from .models import Conversation, Message, Attachment, ChatBotQuery, Appointment

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'content', 'is_read', 'created_at')
    can_delete = False

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0

class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'participants__email', 'participants__username')
    filter_horizontal = ('participants',)
    inlines = [MessageInline]

class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('content', 'sender__email', 'sender__username')
    readonly_fields = ('created_at',)
    inlines = [AttachmentInline]

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'consultant', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('title', 'student__email', 'consultant__email', 'description')
    date_hierarchy = 'date'

admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Attachment)
admin.site.register(ChatBotQuery)
admin.site.register(Appointment, AppointmentAdmin)
