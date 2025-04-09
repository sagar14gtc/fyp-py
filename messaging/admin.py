from django.contrib import admin, messages as django_messages # Rename messages to avoid conflict
from django.shortcuts import redirect
from .models import Conversation, Message, Attachment, ChatBotQuery, Appointment
from .forms import AdminReplyForm # Import the new form
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

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Override change view to add admin reply form."""
        extra_context = extra_context or {}
        conversation = self.get_object(request, object_id)

        if request.method == 'POST' and '_save_reply' in request.POST:
            reply_form = AdminReplyForm(request.POST)
            if reply_form.is_valid():
                content = reply_form.cleaned_data['content']
                if content:
                    # Create the message from the admin
                    Message.objects.create(
                        conversation=conversation,
                        sender=request.user,
                        content=content,
                        is_read=False # Mark as unread for participants
                    )
                    self.message_user(request, "Reply sent successfully.", django_messages.SUCCESS)
                    # Redirect back to the same change view to see the new message
                    return redirect(request.path)
                else:
                    self.message_user(request, "Reply content cannot be empty.", django_messages.ERROR)
            else:
                self.message_user(request, "Error sending reply. Please check the form.", django_messages.ERROR)
        else:
            reply_form = AdminReplyForm()

        extra_context['admin_reply_form'] = reply_form
        extra_context['opts'] = self.model._meta # Required for admin templates
        extra_context['has_change_permission'] = self.has_change_permission(request) # Required for admin templates

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    # Override the default change_form template to include our form
    change_form_template = "admin/messaging/conversation/change_form.html"


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
