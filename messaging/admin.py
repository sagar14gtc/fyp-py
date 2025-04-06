from django.contrib import admin
from .models import Conversation, Message, Attachment, ChatBotQuery, Appointment
from accounts.models import CustomUser # Import CustomUser

# Helper function to check for admin presence in a conversation
def is_admin_in_conversation(conversation):
    if conversation:
        return conversation.participants.filter(role=CustomUser.ADMIN).exists()
    return False

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    # Use the new method to conditionally display content
    fields = ('sender', 'display_content_or_placeholder', 'is_read', 'created_at')
    readonly_fields = ('sender', 'display_content_or_placeholder', 'is_read', 'created_at')
    can_delete = False

    def display_content_or_placeholder(self, obj):
        """Displays content if admin is involved, otherwise placeholder."""
        if obj and is_admin_in_conversation(obj.conversation):
            return obj.content
        return "[Content Hidden]"
    display_content_or_placeholder.short_description = 'Content'

    # Prevent adding new messages directly inline if needed
    # max_num = 0

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0

class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'participants__email', 'participants__username')
    filter_horizontal = ('participants',)
    inlines = [MessageInline] # Uses the modified MessageInline

class MessageAdmin(admin.ModelAdmin):
    # Use the new method name here
    list_display = ('id', 'conversation', 'sender', 'display_content_or_placeholder', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    # Re-enabled 'content' search for admins
    search_fields = ('content', 'sender__email', 'sender__username',)
    # Define fields shown in the detail/change view
    fields = ('conversation', 'sender', 'is_read', 'created_at', 'display_content_or_placeholder')
    # Make placeholder method readonly, along with other non-editable fields
    readonly_fields = ('created_at', 'conversation', 'sender', 'display_content_or_placeholder')
    inlines = [AttachmentInline]

    def display_content_or_placeholder(self, obj):
        """Displays content if admin is involved, otherwise placeholder."""
        if obj and is_admin_in_conversation(obj.conversation):
            return obj.content
        return "[Content Hidden]"
    display_content_or_placeholder.short_description = 'Content' # Sets the column header name

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'consultant', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('title', 'student__email', 'consultant__email', 'description')
    date_hierarchy = 'date'

admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin) # Uses the modified MessageAdmin
admin.site.register(Attachment)
admin.site.register(ChatBotQuery)
admin.site.register(Appointment, AppointmentAdmin)
