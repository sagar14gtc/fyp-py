from django.shortcuts import render, redirect
from django.contrib import messages
from .models import FAQ, Testimonial, ContactMessage, SiteConfiguration
from .forms import ContactForm
from universities.models import University, Program, Country # Import Country model
from django.db.models import Count

def home(request):
    featured_universities = University.objects.filter(is_featured=True).order_by('-ranking') # Removed slice [:6]
    testimonials = Testimonial.objects.filter(is_featured=True).order_by('-created_at')[:3]
    university_count = University.objects.count()
    program_count = Program.objects.count()
    # Get distinct countries that have universities
    countries_with_universities = Country.objects.filter(universities__isnull=False).distinct().order_by('name')
    
    context = {
        'featured_universities': featured_universities,
        'testimonials': testimonials,
        'countries': countries_with_universities, # Add countries to context
        'university_count': university_count,
        'program_count': program_count,
        'university_countries': countries_with_universities.count(), # Count distinct countries
    }
    return render(request, 'core/home.html', context)

def about(request):
    testimonials = Testimonial.objects.filter(is_featured=True).order_by('-created_at')[:6]
    context = {
        'testimonials': testimonials,
    }
    return render(request, 'core/about.html', context)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent! We will get back to you soon.')
            return redirect('core:contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
    }
    return render(request, 'core/contact.html', context)

def faqs(request):
    faqs_list = FAQ.objects.filter(is_published=True).order_by('order', 'category')
    categories = FAQ.objects.filter(is_published=True).values_list('category', flat=True).distinct()
    
    context = {
        'faqs': faqs_list,
        'categories': categories,
    }
    return render(request, 'core/faqs.html', context)

def terms(request):
    return render(request, 'core/terms.html')

def privacy(request):
    return render(request, 'core/privacy.html')
