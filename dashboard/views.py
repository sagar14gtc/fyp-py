from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Count, Sum, Q, F, Case, When, Value, IntegerField
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse_lazy # Import reverse_lazy

from accounts.models import CustomUser
from applications.models import Application, Document, ApplicationStatus
from universities.models import University, Program
from messaging.models import Appointment, Conversation, Message
from notifications.models import Notification # Import Notification model
from django.db.models.functions import TruncMonth, TruncDay
from django.utils.dateparse import parse_date # For parsing date input
# Import forms (will create these later)
# from .forms import ConsultantNotificationForm
# from universities.forms import UniversityForm # Assuming form is in universities app

#import from trained model
import pickle
from django.shortcuts import render
from .forms import RecommendationForm

# --- Helper function to check if user is consultant ---
def is_consultant(user):
    return user.is_authenticated and user.role == 'consultant'

@login_required
def dashboard(request):
    """Main dashboard view customized based on user role."""
    user = request.user

    if user.role == 'student':
        return student_dashboard(request)
    elif user.role == 'consultant':
        return consultant_dashboard(request) # Redirect to the specific consultant view
    elif user.is_staff:
        return admin_dashboard(request)
    else:
        # Default fallback (should ideally not happen for logged-in users)
        messages.error(request, "Unknown user role.")
        return redirect('accounts:login') # Or a generic landing page

def student_dashboard(request):
    """Dashboard view for students."""
    user = request.user

    # Get all student's applications first (unsliced)
    all_applications = Application.objects.filter(student=user)

    # Get application statistics from the full queryset
    application_stats = {
        'total': all_applications.count(),
        'pending': all_applications.filter(status__in=[
            Application.DRAFT, Application.SUBMITTED, Application.PROCESSING,
            Application.DOCUMENTS_REQUIRED, Application.UNDER_REVIEW
        ]).count(),
        'accepted': all_applications.filter(status=Application.ACCEPTED).count(),
        'rejected': all_applications.filter(status=Application.REJECTED).count(),
    }

    # Now get the 5 most recent applications for display
    recent_applications = all_applications.order_by('-application_date')[:5]

    # Get upcoming appointments
    appointments = Appointment.objects.filter(
        student=user,
        date__gte=timezone.now().date(),
        status__in=[Appointment.PENDING, Appointment.CONFIRMED]
    ).order_by('date', 'start_time')[:3]

    # Get unread messages
    unread_messages_count = Message.objects.filter(
        conversation__participants=user,
        is_read=False
    ).exclude(sender=user).count()

    # Get featured universities
    featured_universities = University.objects.filter(is_featured=True) # Removed slice [:4]

    context = {
        'applications': recent_applications, # Pass the sliced list for display
        'application_stats': application_stats,
        'appointments': appointments,
        'unread_messages_count': unread_messages_count,
        'featured_universities': featured_universities, # Renamed variable and context key
        'page_title': 'Student Dashboard'
    }

    return render(request, 'dashboard/student_dashboard.html', context)

@user_passes_test(is_consultant, login_url=reverse_lazy('accounts:login'))
def consultant_dashboard(request):
    """Dashboard view for consultants."""
    user = request.user

    # Quick stats
    assigned_students_count = CustomUser.objects.filter(role='student', applications__consultant=user).distinct().count()
    pending_applications_count = Application.objects.filter(consultant=user, status__in=[Application.SUBMITTED, Application.PROCESSING, Application.DOCUMENTS_REQUIRED]).count()
    upcoming_appointments_count = Appointment.objects.filter(
        consultant=user,
        date__gte=timezone.now().date(),
        status__in=[Appointment.PENDING, Appointment.CONFIRMED]
    ).count()

    context = {
        'assigned_students_count': assigned_students_count,
        'pending_applications_count': pending_applications_count,
        'upcoming_appointments_count': upcoming_appointments_count,
        'page_title': 'Consultant Dashboard'
    }
    # Ensure this view renders the updated consultant dashboard template
    return render(request, 'dashboard/consultant_dashboard.html', context)

def admin_dashboard(request):
    """Dashboard view for admin users."""
    # Overview statistics
    total_students = CustomUser.objects.filter(role='student').count()
    total_consultants = CustomUser.objects.filter(role='consultant').count()
    total_applications = Application.objects.count()
    total_universities = University.objects.count()

    # Application statistics
    application_status_stats = Application.objects.values('status').annotate(count=Count('id'))

    # Get new applications this month
    this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_applications_this_month = Application.objects.filter(application_date__gte=this_month).count()

    # Get new users this month
    new_users_this_month = CustomUser.objects.filter(date_joined__gte=this_month).count()

    # Recent activity
    recent_applications = Application.objects.order_by('-application_date')[:5]
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]

    context = {
        'total_students': total_students,
        'total_consultants': total_consultants,
        'total_applications': total_applications,
        'total_universities': total_universities,
        'application_status_stats': application_status_stats,
        'new_applications_this_month': new_applications_this_month,
        'new_users_this_month': new_users_this_month,
        'recent_applications': recent_applications,
        'recent_users': recent_users,
        'page_title': 'Admin Dashboard'
    }

    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def student_list(request):
    """View to list all students. Accessible to staff and consultants."""
    user = request.user

    if not (user.is_staff or user.role == 'consultant'): # Correct indentation
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard:dashboard') # Use namespaced URL

    students_qs = CustomUser.objects.filter(role='student') # Correct indentation

    # If consultant, only show students assigned to them
    if user.role == 'consultant': # Correct indentation
        students_qs = students_qs.filter(applications__consultant=user).distinct()

    # Filter by search query if provided
    search_query = request.GET.get('q') # Correct indentation
    if search_query: # Correct indentation
        students_qs = students_qs.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # Paginate results
    paginator = Paginator(students_qs.order_by('-date_joined'), 20)  # 20 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'students': page_obj,
        'search_query': search_query,
        'page_title': 'Student Directory'
    }

    # Consider a different template for consultants if needed
    # template = 'dashboard/consultant/student_list.html' if user.role == 'consultant' else 'dashboard/student_list.html'
    return render(request, 'dashboard/student_list.html', context) # Using shared template for now

@login_required
def student_detail(request, user_id):
    """View details of a specific student."""
    user = request.user

    if not (user.is_staff or user.role == 'consultant'):
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard:dashboard') # Use namespaced URL

    student = get_object_or_404(CustomUser, id=user_id, role='student')

    # If consultant, check if they are assigned to this student?
    # is_assigned = Application.objects.filter(student=student, consultant=user).exists()
    # if user.role == 'consultant' and not is_assigned and not user.is_staff:
    #     messages.error(request, "You are not assigned to this student.")
    #     return redirect('dashboard:student_list')

    # Get student's applications (maybe filter for consultant?)
    applications = Application.objects.filter(student=student).order_by('-application_date')
    if user.role == 'consultant':
        applications = applications.filter(consultant=user) # Show only apps managed by this consultant

    # Get student's appointments (maybe filter for consultant?)
    appointments = Appointment.objects.filter(student=student).order_by('-date')
    if user.role == 'consultant':
        appointments = appointments.filter(consultant=user) # Show only appointments with this consultant

    context = {
        'student': student,
        'applications': applications,
        'appointments': appointments,
        'page_title': f'Student: {student.get_full_name() or student.username}'
    }
    # Revert to the original path, assuming DIRS setting finds it
    return render(request, 'dashboard/student_detail.html', context)

@login_required
def consultant_list(request):
    """View to list all consultants. Only accessible to staff."""
    user = request.user

    if not user.is_staff:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard:dashboard') # Use namespaced URL

    consultants = CustomUser.objects.filter(role='consultant')

    # Filter by search query if provided
    search_query = request.GET.get('q')
    if search_query:
        consultants = consultants.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # Paginate results
    paginator = Paginator(consultants.order_by('-date_joined'), 20)  # 20 consultants per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'consultants': page_obj,
        'search_query': search_query,
        'page_title': 'Consultant Directory'
    }

    return render(request, 'dashboard/consultant_list.html', context)

@login_required
def consultant_detail(request, user_id):
    """View details of a specific consultant."""
    user = request.user

    if not user.is_staff:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard:dashboard') # Use namespaced URL

    consultant = get_object_or_404(CustomUser, id=user_id, role='consultant')

    # Get consultant's assigned applications
    applications = Application.objects.filter(consultant=consultant).order_by('-application_date')

    # Get consultant's appointments
    appointments = Appointment.objects.filter(consultant=consultant).order_by('-date')

    # Get application statistics
    application_stats = {
        'total': applications.count(),
        'accepted': applications.filter(status=Application.ACCEPTED).count(),
        'rejected': applications.filter(status=Application.REJECTED).count(),
        'in_progress': applications.exclude(
            status__in=[Application.ACCEPTED, Application.REJECTED, Application.CANCELED, Application.ENROLLMENT_CONFIRMED]
        ).count(),
    }

    context = {
        'consultant': consultant,
        'applications': applications,
        'appointments': appointments,
        'application_stats': application_stats,
        'page_title': f'Consultant: {consultant.get_full_name() or consultant.username}'
    }

    return render(request, 'dashboard/consultant_detail.html', context)

@login_required
def application_overview(request):
    """View overall application statistics. Accessible to staff and consultants."""
    user = request.user

    if not (user.is_staff or user.role == 'consultant'):
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard:dashboard') # Use namespaced URL

    # Base queryset, filtered for consultants
    applications = Application.objects.all()
    if user.role == 'consultant':
        applications = applications.filter(consultant=user)

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter and status_filter in [choice[0] for choice in Application.STATUS_CHOICES]:
        applications = applications.filter(status=status_filter)

    # Filter by university if provided
    university_filter = request.GET.get('university')
    if university_filter:
        applications = applications.filter(program__university_id=university_filter)

    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        applications = applications.filter(application_date__gte=start_date)
    if end_date:
        applications = applications.filter(application_date__lte=end_date)

    # Get application statistics
    status_stats = applications.values('status').annotate(count=Count('id'))

    # Get monthly application data for chart
    monthly_data = applications.annotate(
        month=TruncMonth('application_date')
    ).values('month').annotate(count=Count('id')).order_by('month')

    # Get university data for chart
    university_data = applications.values(
        'program__university__name'
    ).annotate(count=Count('id')).order_by('-count')[:10]

    # Paginate applications for display
    paginator = Paginator(applications.order_by('-application_date'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get universities for filter
    universities = University.objects.all()

    context = {
        'applications': page_obj,
        'status_stats': status_stats,
        'monthly_data': monthly_data,
        'university_data': university_data,
        'universities': universities,
        'status_choices': Application.STATUS_CHOICES,
        'current_status': status_filter,
        'current_university': university_filter,
        'start_date': start_date,
        'end_date': end_date,
        'page_title': 'Application Overview'
    }

    return render(request, 'dashboard/application_overview.html', context)

@login_required
def analytics(request):
    """View analytics dashboard. Only accessible to staff."""
    user = request.user

    if not user.is_staff:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard:dashboard') # Use namespaced URL

    # Date range filtering
    start_date = request.GET.get('start_date', (timezone.now() - timezone.timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))

    # Application statistics
    applications = Application.objects.filter(
        application_date__gte=start_date,
        application_date__lte=end_date
    )

    # User registration statistics
    new_users = CustomUser.objects.filter(
        date_joined__gte=start_date,
        date_joined__lte=end_date
    )

    # Application status distribution
    status_distribution = applications.values('status').annotate(count=Count('id'))

    # Daily application trends
    daily_trends = applications.annotate(
        day=TruncDay('application_date')
    ).values('day').annotate(count=Count('id')).order_by('day')

    # Top universities by application count
    top_universities = applications.values(
        'program__university__name'
    ).annotate(count=Count('id')).order_by('-count')[:10]

    # Top programs by application count
    top_programs = applications.values(
        'program__name',
        'program__university__name'
    ).annotate(count=Count('id')).order_by('-count')[:10]

    # User registration trend
    user_registration_trend = new_users.annotate(
        day=TruncDay('date_joined')
    ).values('day').annotate(count=Count('id')).order_by('day')

    # Acceptance rate by university
    acceptance_rate = applications.values(
        'program__university__name'
    ).annotate(
        total=Count('id'),
        accepted=Count(Case(When(status=Application.ACCEPTED, then=1), output_field=IntegerField()))
    ).annotate(
        rate=F('accepted') * 100.0 / F('total')
    ).order_by('-total')[:10]

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'applications_count': applications.count(),
        'new_users_count': new_users.count(),
        'status_distribution': status_distribution,
        'daily_trends': daily_trends,
        'top_universities': top_universities,
        'top_programs': top_programs,
        'user_registration_trend': user_registration_trend,
        'acceptance_rate': acceptance_rate,
        'page_title': 'Analytics Dashboard'
    }

    return render(request, 'dashboard/analytics.html', context)

@login_required
def notifications(request):
    """View user notifications."""
    user = request.user

    # Get unread notifications
    unread_notifications = Notification.objects.filter(
        recipient=user,
        unread=True
    ).order_by('-timestamp')

    # Get read notifications
    read_notifications = Notification.objects.filter(
        recipient=user,
        unread=False
    ).order_by('-timestamp')[:20]  # Limit to recent 20 read notifications

    context = {
        'unread_notifications': unread_notifications,
        'read_notifications': read_notifications,
        'page_title': 'Notifications'
    }

    return render(request, 'dashboard/notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.unread = False
    notification.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest': # Check for AJAX request
        return JsonResponse({'success': True})

    return redirect('dashboard:notifications')

@login_required
def activity_log(request):
    """View activity log. Only accessible to staff."""
    user = request.user

    if not user.is_staff:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard:dashboard') # Use namespaced URL

    # Get application status changes
    application_status_changes = ApplicationStatus.objects.all().order_by('-changed_at')[:50]

    # Get recent user registrations
    recent_registrations = CustomUser.objects.order_by('-date_joined')[:20]

    # Get recent application submissions
    recent_submissions = Application.objects.exclude(
        status=Application.DRAFT
    ).order_by('-application_date')[:20]

    context = {
        'application_status_changes': application_status_changes,
        'recent_registrations': recent_registrations,
        'recent_submissions': recent_submissions,
        'page_title': 'Activity Log'
    }

    return render(request, 'dashboard/activity_log.html', context)


from django.db.models import Prefetch # Import Prefetch

@login_required
def university_search(request):
    """View for searching universities and their programs."""

    # Get filter parameters from GET request
    uni_name = request.GET.get('uni_name', '')
    country_name = request.GET.get('country_name', '')
    program_name = request.GET.get('program_name', '') # Using program name as subject proxy
    degree_type = request.GET.get('degree_type', '')
    intake_after = request.GET.get('intake_after', '')
    max_fee_usd_str = request.GET.get('max_fee_usd', '') # Get fee as string

    # Start with all universities, prefetching all programs initially
    universities_qs = University.objects.select_related('city', 'country').prefetch_related(
        Prefetch('programs', queryset=Program.objects.all().order_by('name'), to_attr='all_programs')
    ).distinct() # Use distinct if filtering on related models causes duplicates

    # Filter Universities based on direct University fields
    if uni_name:
        universities_qs = universities_qs.filter(name__icontains=uni_name)
    if country_name:
        # Assuming country_name is the name, not ID. Adjust if it's ID.
        universities_qs = universities_qs.filter(country__name__icontains=country_name)

    # Filter by Max Fee (University level)
    max_fee_value = None
    if max_fee_usd_str:
        try:
            from decimal import Decimal, InvalidOperation
            max_fee_value = Decimal(max_fee_usd_str)
            if max_fee_value >= 0:
                 # Apply filter only if fee is valid and non-negative
                 # This implicitly handles fee_usd being NULL as NULL <= value is false
                 universities_qs = universities_qs.filter(fee_usd__lte=max_fee_value)
            else:
                messages.warning(request, "Maximum fee must be a non-negative number.")
                max_fee_value = None # Reset if negative
        except InvalidOperation:
            messages.warning(request, "Invalid maximum fee format. Please enter a number.")
            max_fee_value = None # Reset if invalid format

    # Prepare program filters separately
    program_filters = Q()
    if program_name:
        program_filters &= Q(name__icontains=program_name)
    if degree_type:
        program_filters &= Q(degree_type=degree_type)
    if intake_after:
        try:
            intake_date = parse_date(intake_after)
            if intake_date:
                program_filters &= Q(start_date__gte=intake_date)
            else:
                 messages.warning(request, "Invalid intake date format. Please use YYYY-MM-DD.")
        except ValueError:
             messages.warning(request, "Invalid intake date format. Please use YYYY-MM-DD.")


    # If there are program filters, we need to filter universities based on whether they HAVE matching programs
    if program_filters != Q(): # Check if any program filters were actually added
         universities_qs = universities_qs.filter(programs__in=Program.objects.filter(program_filters)).distinct()

    # Now, iterate through the filtered universities and attach *only* the matching programs
    # This requires another loop but ensures we only show relevant programs per university
    results = []
    for uni in universities_qs:
        # Apply program filters if they exist
        if program_filters != Q():
            matching_programs = [p for p in uni.all_programs if Program.objects.filter(pk=p.pk).filter(program_filters).exists()]
        else:
            matching_programs = uni.all_programs # Show all programs if no filters

        # Only include the university if it has matching programs (when program filters are active)
        # Or always include if no program filters are active
        if matching_programs or program_filters == Q():
            uni.filtered_programs = matching_programs # Attach the filtered list
            results.append(uni)

    # Paginate the final list of universities
    paginator = Paginator(results, 10) # 10 universities per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'universities': page_obj, # Pass paginated universities
        'page_title': 'University Search',
        'degree_types': Program.DEGREE_TYPES, # Pass choices for dropdown
        # Pass filter values back to template to repopulate form
        'uni_name': uni_name,
        'country_name': country_name,
        'program_name': program_name,
        'degree_type': degree_type,
        'intake_after': intake_after,
        'max_fee_usd': max_fee_usd_str, # Pass the original string back to preserve input
    }
    return render(request, 'dashboard/university_search.html', context)


# --- New Consultant Specific Views ---

@user_passes_test(is_consultant, login_url=reverse_lazy('accounts:login'))
def consultant_application_list(request):
    """List applications assigned to the current consultant."""
    user = request.user
    applications = Application.objects.filter(consultant=user).select_related(
        'student', 'program', 'program__university'
    ).order_by('-application_date')

    # Add filtering/searching if needed
    status_filter = request.GET.get('status')
    student_search = request.GET.get('student')

    if status_filter:
        applications = applications.filter(status=status_filter)
    if student_search:
        applications = applications.filter(
            Q(student__username__icontains=student_search) |
            Q(student__first_name__icontains=student_search) |
            Q(student__last_name__icontains=student_search) |
            Q(student__email__icontains=student_search)
        )

    paginator = Paginator(applications, 20) # 20 applications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'applications': page_obj,
        'status_choices': Application.STATUS_CHOICES,
        'current_status': status_filter,
        'student_search': student_search,
        'page_title': 'My Assigned Applications'
    }
    # Need to create this template: templates/dashboard/consultant/application_list.html
    return render(request, 'dashboard/consultant/application_list.html', context)

# --- Recommendation System View ---
# Load the model once when the app starts (more efficient)
MODEL_PATH = 'dashboard/models/university_recommendation_model.pkl'
with open(MODEL_PATH, 'rb') as file:
    RECOMMENDATION_MODEL = pickle.load(file)

def recommend_universities(request):
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            # Extract input data
            gre_verbal = form.cleaned_data['gre_verbal']
            gre_quant = form.cleaned_data['gre_quant']
            gre_awa = form.cleaned_data['gre_awa']
            gpa = form.cleaned_data['gpa']

            # Prepare input for the model
            input_data = [[gre_verbal, gre_quant, gre_awa, gpa]]

            # Get predictions
            predictions = RECOMMENDATION_MODEL.predict(input_data)

            # Render results with raw predictions
            return render(request, 'dashboard/recommendations.html', {
                'recommendations': predictions # Pass the raw predictions list
            })
    else:
        form = RecommendationForm()

    return render(request, 'dashboard/recommendation_form.html', {'form': form})
