from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import University, Program, Faculty, Country

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
