from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Prefetch, Max, Count

from .models import Conversation, Message, Attachment, ChatBotQuery, Appointment
from .forms import MessageForm, AppointmentForm, ChatbotQueryForm, AttachmentForm
from accounts.models import CustomUser

@login_required
def conversation_list(request):
    """View to list all conversations of the current user."""
    user = request.user

    # Get all conversations the user is participating in
    conversations = Conversation.objects.filter(participants=user)

    # Annotate conversations with latest message and unread count
    conversations = conversations.annotate(
        latest_message_time=Max('messages__created_at'),
        unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=user))
    ).order_by('-latest_message_time')

    context = {
        'conversations': conversations,
        'page_title': 'Messages'
    }
    return render(request, 'messaging/conversation_list.html', context)

@login_required
def new_conversation(request):
    """View to start a new conversation."""
    user = request.user

    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        message_content = request.POST.get('content')

        try:
            recipient = CustomUser.objects.get(id=recipient_id)

            # Check if conversation already exists
            existing_conversation = Conversation.objects.filter(participants=user).filter(participants=recipient)

            if existing_conversation.exists() and existing_conversation.count() == 1:
                conversation = existing_conversation.first()
            else:
                # Create new conversation
                conversation = Conversation.objects.create()
                conversation.participants.add(user, recipient)

                # Set title based on recipient name
                if recipient.role == 'consultant':
                    conversation.title = f"Consultation with {recipient.get_full_name() or recipient.username}"
                else:
                    conversation.title = f"Conversation with {recipient.get_full_name() or recipient.username}"
                conversation.save()

            # Create message
            if message_content:
                message = Message.objects.create(
                    conversation=conversation,
                    sender=user,
                    content=message_content
                )

                # Handle file attachments
                files = request.FILES.getlist('attachments')
                for file in files:
                    Attachment.objects.create(
                        message=message,
                        file=file,
                        name=file.name
                    )

            messages.success(request, "Message sent successfully!")
            return redirect('messaging:conversation_detail', conversation_id=conversation.id)

        except CustomUser.DoesNotExist:
            messages.error(request, "Recipient not found.")

    # Get potential recipients
    if user.role == 'student':
        # Students can message consultants or staff
        recipients = CustomUser.objects.filter(Q(role='consultant') | Q(is_staff=True))
    elif user.role == 'consultant':
        # Consultants can message students they are assigned to and staff
        recipients = CustomUser.objects.filter(
            Q(role='student', applications__consultant=user) | Q(is_staff=True)
        ).distinct()
    else:
        # Staff can message anyone
        recipients = CustomUser.objects.exclude(id=user.id)

    context = {
        'recipients': recipients,
        'page_title': 'New Message'
    }
    return render(request, 'messaging/new_conversation.html', context)

@login_required
def conversation_detail(request, conversation_id):
    """View to see details of a specific conversation."""
    user = request.user
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Check if user is a participant in this conversation
    if user not in conversation.participants.all():
        raise PermissionDenied("You don't have permission to view this conversation.")

    # Get all messages in this conversation
    messages_list = conversation.messages.all().select_related('sender').prefetch_related('attachments')

    # Mark messages as read
    unread_messages = messages_list.filter(is_read=False).exclude(sender=user)
    for msg in unread_messages:
        msg.is_read = True
        msg.save()

    # Get the other participant
    other_participants = conversation.participants.exclude(id=user.id)

    # Prepare message form
    message_form = MessageForm()
    attachment_form = AttachmentForm()

    context = {
        'conversation': conversation,
        'messages': messages_list,
        'other_participants': other_participants,
        'message_form': message_form,
        'attachment_form': attachment_form,
        'page_title': conversation.title or 'Conversation'
    }
    return render(request, 'messaging/conversation_detail.html', context)

@login_required
def send_message(request, conversation_id):
    """View to send a message in a conversation."""
    user = request.user
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Check if user is a participant in this conversation
    if user not in conversation.participants.all():
        raise PermissionDenied("You don't have permission to send messages in this conversation.")

    if request.method == 'POST':
        form = MessageForm(request.POST)

        if form.is_valid():
            message_content = form.cleaned_data['content']

            if message_content:
                # Create message
                message = Message.objects.create(
                    conversation=conversation,
                    sender=user,
                    content=message_content
                )

                # Handle attachments
                files = request.FILES.getlist('attachments')
                for file in files:
                    Attachment.objects.create(
                        message=message,
                        file=file,
                        name=file.name
                    )

                # Update conversation last activity time
                conversation.updated_at = timezone.now()
                conversation.save()

                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message_id': message.id,
                        'sender': user.get_full_name() or user.username,
                        'content': message.content,
                        'created_at': message.created_at.strftime('%Y-%m-%d %H:%M'),
                        'attachments': [{'name': a.name, 'url': a.file.url} for a in message.attachments.all()]
                    })

                messages.success(request, "Message sent successfully!")
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Message cannot be empty'})
                messages.error(request, "Message cannot be empty.")
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            messages.error(request, "There was an error sending your message.")

    return redirect('messaging:conversation_detail', conversation_id=conversation.id)

@login_required
def chatbot(request):
    """View for chatbot interaction."""
    user = request.user

    # Get previous queries
    previous_queries = ChatBotQuery.objects.filter(user=user).order_by('-created_at')[:10]

    if request.method == 'POST':
        form = ChatbotQueryForm(request.POST)

        if form.is_valid():
            query = form.cleaned_data['query']

            # TODO: Add actual chatbot integration here
            # For now, just return a placeholder response
            response = "Thank you for your question. This is a placeholder response as the chatbot is still under development. Please contact our support team for accurate information."

            # Save the query and response
            chat_query = ChatBotQuery.objects.create(
                user=user,
                query=query,
                response=response
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'query': chat_query.query,
                    'response': chat_query.response,
                    'created_at': chat_query.created_at.strftime('%Y-%m-%d %H:%M')
                })

            messages.success(request, "Query sent to chatbot.")
            return redirect('messaging:chatbot')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            messages.error(request, "There was an error with your query.")
    else:
        form = ChatbotQueryForm()

    context = {
        'form': form,
        'previous_queries': previous_queries,
        'page_title': 'UniBot - Your Virtual Assistant'
    }
    return render(request, 'messaging/chatbot.html', context)

@login_required
def appointment_list(request):
    """View to list all appointments for the current user."""
    user = request.user

    if user.role == 'student':
        appointments = Appointment.objects.filter(student=user).order_by('date', 'start_time')
    elif user.role == 'consultant':
        appointments = Appointment.objects.filter(consultant=user).order_by('date', 'start_time')
    else:
        # Staff can see all appointments
        appointments = Appointment.objects.all().order_by('date', 'start_time')

    # Filter by status if provided
    status = request.GET.get('status')
    if status and status in [choice[0] for choice in Appointment.STATUS_CHOICES]:
        appointments = appointments.filter(status=status)

    # Filter by date if provided
    date_filter = request.GET.get('date')
    if date_filter:
        appointments = appointments.filter(date=date_filter)

    context = {
        'appointments': appointments,
        'status_choices': Appointment.STATUS_CHOICES,
        'current_status': status,
        'page_title': 'My Appointments'
    }
    return render(request, 'messaging/appointment_list.html', context)

@login_required
def create_appointment(request):
    """View to create a new appointment."""
    user = request.user

    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=user)

        if form.is_valid():
            appointment = form.save(commit=False)

            # Assign student and consultant based on user role and form data
            if user.role == 'student':
                appointment.student = user
                # Get the selected consultant from the form
                appointment.consultant = form.cleaned_data.get('consultant')
            elif user.role == 'consultant':
                appointment.consultant = user
                # Get the selected student from the form
                appointment.student = form.cleaned_data.get('student')
            elif user.is_staff:
                # Staff selects both student and consultant in the form
                appointment.student = form.cleaned_data.get('student')
                appointment.consultant = form.cleaned_data.get('consultant')

            # Ensure both student and consultant are assigned before saving
            if appointment.student and appointment.consultant:
                appointment.save()
                messages.success(request, "Appointment created successfully!")
                # Redirect to the appointment list after creation
                return redirect('messaging:appointment_list')
            else:
                # Handle error if student or consultant is missing (shouldn't happen with proper form validation)
                messages.error(request, "Could not create appointment. Missing student or consultant information.")
                # Re-render the form with errors if necessary (though form validation should catch this)
                # Fall through to render the form again below

        # If form is not valid, fall through to render the form with errors

    else: # Handle GET request
        form = AppointmentForm(user=user)

    context = {
        'form': form,
        'page_title': 'Schedule Appointment'
    }
    return render(request, 'messaging/create_appointment.html', context)


@login_required
def appointment_detail(request, appointment_id):
    """View to see details of a specific appointment."""
    user = request.user
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Check if user has permission to view this appointment
    if user not in [appointment.student, appointment.consultant] and not user.is_staff:
        raise PermissionDenied("You don't have permission to view this appointment.")

    context = {
        'appointment': appointment,
        'page_title': f'Appointment: {appointment.title}'
    }
    return render(request, 'messaging/appointment_detail.html', context)

@login_required
def update_appointment(request, appointment_id):
    """View to update an existing appointment."""
    user = request.user
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Check if user has permission to update this appointment
    if user not in [appointment.student, appointment.consultant] and not user.is_staff:
        raise PermissionDenied("You don't have permission to update this appointment.")

    # Don't allow updating completed or cancelled appointments
    if appointment.status in [Appointment.COMPLETED, Appointment.CANCELLED]:
        messages.error(request, "Cannot update completed or cancelled appointments.")
        return redirect('messaging:appointment_detail', appointment_id=appointment.id)

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment, user=user)

        if form.is_valid():
            # Mark as rescheduled if date or time changed
            if (appointment.date != form.cleaned_data['date'] or
                appointment.start_time != form.cleaned_data['start_time'] or
                appointment.end_time != form.cleaned_data['end_time']):
                form.instance.status = Appointment.RESCHEDULED

            form.save()
            messages.success(request, "Appointment updated successfully!")
            return redirect('messaging:appointment_detail', appointment_id=appointment.id)
    else:
        form = AppointmentForm(instance=appointment, user=user)

    context = {
        'form': form,
        'appointment': appointment,
        'page_title': f'Update Appointment: {appointment.title}'
    }
    return render(request, 'messaging/update_appointment.html', context)

@login_required
def cancel_appointment(request, appointment_id):
    """View to cancel an appointment."""
    user = request.user
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Check if user has permission to cancel this appointment
    if user not in [appointment.student, appointment.consultant] and not user.is_staff:
        raise PermissionDenied("You don't have permission to cancel this appointment.")

    # Don't allow cancelling completed appointments
    if appointment.status == Appointment.COMPLETED:
        messages.error(request, "Cannot cancel completed appointments.")
        return redirect('messaging:appointment_detail', appointment_id=appointment.id)

    if request.method == 'POST':
        appointment.status = Appointment.CANCELLED
        appointment.save()

        messages.success(request, "Appointment cancelled successfully.")
        return redirect('messaging:appointment_list')

    context = {
        'appointment': appointment,
        'page_title': 'Cancel Appointment'
    }
    return render(request, 'messaging/cancel_appointment.html', context)

@login_required
def mark_messages_read(request, conversation_id):
    """API view to mark all messages in a conversation as read."""
    user = request.user
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Check if user is a participant in this conversation
    if user not in conversation.participants.all():
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    # Mark all messages not sent by the user as read
    unread_messages = Message.objects.filter(
        conversation=conversation,
        is_read=False
    ).exclude(sender=user)

    unread_count = unread_messages.count()
    unread_messages.update(is_read=True)

    return JsonResponse({'success': True, 'marked_read': unread_count})
