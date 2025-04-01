from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q

from .forms import CustomUserCreationForm, CustomUserChangeForm, StudentProfileForm, ConsultantProfileForm
from .models import CustomUser, StudentProfile, ConsultantProfile
from applications.models import Application # Import Application model
from messaging.models import Message # Import Message model

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    context = {'user': user}
    
    # Get base profile and unread message count (common to all roles)
    unread_count = Message.objects.filter(
        conversation__participants=user,
        is_read=False
    ).exclude(sender=user).count()
    context['unread_count'] = unread_count

    if user.role == CustomUser.STUDENT:
        profile, created = StudentProfile.objects.get_or_create(user=user)
        context['profile'] = profile
        
        # Calculate application stats for students
        student_applications = Application.objects.filter(student=user)
        application_stats = {
            'total': student_applications.count(),
            'pending': student_applications.filter(status__in=[
                Application.DRAFT, Application.SUBMITTED, Application.PROCESSING,
                Application.DOCUMENTS_REQUIRED, Application.UNDER_REVIEW
            ]).count(),
            'accepted': student_applications.filter(status=Application.ACCEPTED).count(),
            'rejected': student_applications.filter(status=Application.REJECTED).count(),
        }
        context['application_stats'] = application_stats

    elif user.role == CustomUser.CONSULTANT:
        profile, created = ConsultantProfile.objects.get_or_create(user=user)
        context['profile'] = profile
        
        # Get assigned students for consultants
        # Assuming applications link students to consultants
        assigned_student_ids = Application.objects.filter(
            consultant=user
        ).values_list('student_id', flat=True).distinct()
        
        assigned_students = CustomUser.objects.filter(
            id__in=assigned_student_ids
        ).annotate(
            applications_count=Count('applications', filter=Q(applications__consultant=user))
        )
        context['assigned_students'] = assigned_students

    else: # Admin or other roles
        context['profile'] = None # No specific profile model for admin
    
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    user = request.user
    
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        
        if user.role == CustomUser.STUDENT:
            profile, created = StudentProfile.objects.get_or_create(user=user)
            profile_form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        elif user.role == CustomUser.CONSULTANT:
            profile, created = ConsultantProfile.objects.get_or_create(user=user)
            profile_form = ConsultantProfileForm(request.POST, instance=profile)
        else:
            profile_form = None
            
        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
    else:
        user_form = CustomUserChangeForm(instance=user)
        
        if user.role == CustomUser.STUDENT:
            profile, created = StudentProfile.objects.get_or_create(user=user)
            profile_form = StudentProfileForm(instance=profile)
        elif user.role == CustomUser.CONSULTANT:
            profile, created = ConsultantProfile.objects.get_or_create(user=user)
            profile_form = ConsultantProfileForm(instance=profile)
        else:
            profile_form = None
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'accounts/edit_profile.html', context)
