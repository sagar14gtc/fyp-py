from django.shortcuts import render, get_object_or_404, redirect # Add redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test # Add decorators
from django.urls import reverse_lazy # Add reverse_lazy
from django.contrib import messages # Add messages
from django.core.paginator import Paginator # Add Paginator

from .models import University, Program, Faculty, Country
# Assuming UniversityForm exists or will be created in universities/forms.py
# from .forms import UniversityForm

# --- Helper function to check if user is consultant ---
# (Copied from dashboard.views for now, consider moving to a shared utils module)
def is_consultant(user):
    return user.is_authenticated and user.role == 'consultant'

# --- Existing Views ---

def university_list(request):
    """View to list all universities."""
    universities = University.objects.all().order_by('name')
    featured_universities = University.objects.filter(is_featured=True)[:6]
    countries = Country.objects.all()

    context = {
        'universities': universities,
        'featured_universities': featured_universities,
        'countries': countries,
        'page_title': 'Explore Universities'
    }
    return render(request, 'universities/university_list.html', context)

def university_detail(request, slug):
    """View to show details of a specific university."""
    university = get_object_or_404(University, slug=slug)
    programs = university.programs.all().order_by('name')
    faculties = university.faculties.all().order_by('name')

    # Group programs by degree type
    bachelor_programs = programs.filter(degree_type=Program.BACHELOR)
    master_programs = programs.filter(degree_type=Program.MASTER)
    phd_programs = programs.filter(degree_type=Program.PHD)
    other_programs = programs.exclude(
        degree_type__in=[Program.BACHELOR, Program.MASTER, Program.PHD]
    )

    context = {
        'university': university,
        'programs': programs,
        'faculties': faculties,
        'bachelor_programs': bachelor_programs,
        'master_programs': master_programs,
        'phd_programs': phd_programs,
        'other_programs': other_programs,
        'page_title': university.name
    }
    return render(request, 'universities/university_detail.html', context)

def program_list(request, uni_slug):
    """View to list all programs for a specific university."""
    university = get_object_or_404(University, slug=uni_slug)
    programs = university.programs.all().order_by('name')

    # Filter by degree type if specified
    degree_type = request.GET.get('degree_type')
    if degree_type:
        programs = programs.filter(degree_type=degree_type)

    # Filter by faculty if specified
    faculty_id = request.GET.get('faculty')
    if faculty_id:
        programs = programs.filter(faculty_id=faculty_id)

    faculties = university.faculties.all()

    context = {
        'university': university,
        'programs': programs,
        'faculties': faculties,
        'degree_types': Program.DEGREE_TYPES,
        'page_title': f'Programs at {university.name}'
    }
    return render(request, 'universities/program_list.html', context)

def program_detail(request, uni_slug, prog_slug):
    """View to show details of a specific program."""
    university = get_object_or_404(University, slug=uni_slug)
    program = get_object_or_404(Program, slug=prog_slug, university=university)
    requirements = program.requirements.all()

    # Related programs (same degree type at the same university)
    related_programs = university.programs.filter(
        degree_type=program.degree_type
    ).exclude(id=program.id)[:4]

    context = {
        'university': university,
        'program': program,
        'requirements': requirements,
        'related_programs': related_programs,
        'page_title': f'{program.name} - {university.name}'
    }
    return render(request, 'universities/program_detail.html', context)

@login_required # Add this decorator
def search_universities(request):
    """View to search for universities by name, country, or program."""
    query = request.GET.get('q', '')
    universities = University.objects.all()

    if query:
        universities = universities.filter(
            Q(name__icontains=query) |
            Q(country__name__icontains=query) |
            Q(city__name__icontains=query) |
            Q(programs__name__icontains=query)
        ).distinct()

    context = {
        'universities': universities,
        'query': query,
        'page_title': 'Search Results'
    }
    return render(request, 'universities/search_results.html', context)

def filter_universities(request):
    """View to filter universities by various criteria."""
    universities = University.objects.all()

    # Filter by country
    country_id = request.GET.get('country')
    if country_id:
        universities = universities.filter(country_id=country_id)

    # Filter by ranking range
    min_ranking = request.GET.get('min_ranking')
    max_ranking = request.GET.get('max_ranking')
    if min_ranking:
        universities = universities.filter(ranking__gte=min_ranking)
    if max_ranking:
        universities = universities.filter(ranking__lte=max_ranking)

    # Filter by program degree type
    degree_type = request.GET.get('degree_type')
    if degree_type:
        universities = universities.filter(programs__degree_type=degree_type).distinct()

    # Get filter options for the form
    countries = Country.objects.all()

    context = {
        'universities': universities,
        'countries': countries,
        'degree_types': Program.DEGREE_TYPES,
        'selected_country': country_id,
        'selected_degree_type': degree_type,
        'min_ranking': min_ranking,
        'max_ranking': max_ranking,
        'page_title': 'Filter Universities'
    }
    return render(request, 'universities/filter_universities.html', context)

def compare_universities(request):
    """View to compare multiple universities side by side."""
    university_ids = request.GET.getlist('university_ids')
    universities = University.objects.filter(id__in=university_ids)

    # If no universities selected yet, show a form to select universities
    if not university_ids:
        all_universities = University.objects.all().order_by('name')
        context = {
            'all_universities': all_universities,
            'page_title': 'Compare Universities'
        }
        return render(request, 'universities/compare_form.html', context)

    context = {
        'universities': universities,
        'page_title': 'University Comparison'
    }
    return render(request, 'universities/compare_universities.html', context)


# --- New Consultant Specific Views ---

@user_passes_test(is_consultant, login_url=reverse_lazy('accounts:login'))
def consultant_university_list(request):
    """List universities for consultant management."""
    universities_qs = University.objects.all().order_by('name')

    # Add search/filtering if needed
    search_query = request.GET.get('q')
    if search_query:
        universities_qs = universities_qs.filter(
            Q(name__icontains=search_query) |
            Q(country__name__icontains=search_query) |
            Q(city__name__icontains=search_query)
        )

    paginator = Paginator(universities_qs, 20) # 20 universities per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'universities': page_obj,
        'search_query': search_query,
        'page_title': 'Manage Universities'
    }
    # Need to create this template: templates/universities/consultant/university_list.html
    return render(request, 'universities/consultant/university_list.html', context)

@user_passes_test(is_consultant, login_url=reverse_lazy('accounts:login'))
def consultant_add_university(request):
    """Add a new university (Consultant view)."""
    # Need UniversityForm
    try:
        from .forms import UniversityForm # Assuming it exists
    except ImportError:
        messages.error(request, "UniversityForm not found. Please create it in universities/forms.py.")
        return redirect('universities:consultant_university_list')


    if request.method == 'POST':
        form = UniversityForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "University added successfully.")
            return redirect('universities:consultant_university_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UniversityForm()

    context = {
        'form': form,
        'page_title': 'Add New University'
    }
    # Need to create this template: templates/universities/consultant/university_form.html
    return render(request, 'universities/consultant/university_form.html', context)

@user_passes_test(is_consultant, login_url=reverse_lazy('accounts:login'))
def consultant_edit_university(request, uni_id):
    """Edit an existing university (Consultant view)."""
    # Need UniversityForm
    try:
        from .forms import UniversityForm # Assuming it exists
    except ImportError:
        messages.error(request, "UniversityForm not found. Please create it in universities/forms.py.")
        return redirect('universities:consultant_university_list')

    university = get_object_or_404(University, id=uni_id)

    if request.method == 'POST':
        form = UniversityForm(request.POST, request.FILES, instance=university)
        if form.is_valid():
            form.save()
            messages.success(request, f"University '{university.name}' updated successfully.")
            return redirect('dashboard:consultant_university_list') # Corrected namespace
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UniversityForm(instance=university)

    context = {
        'form': form,
        'university': university,
        'page_title': f'Edit University: {university.name}'
    }
    # Re-use the form template
    return render(request, 'universities/consultant/university_form.html', context)
