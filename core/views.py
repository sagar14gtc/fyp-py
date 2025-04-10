from django.shortcuts import render, redirect
from django.contrib import messages
from .models import FAQ, Testimonial, ContactMessage, SiteConfiguration
from .forms import ContactForm
from universities.models import University, Program, Country # Import Country model
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import os
import google.generativeai as genai # Import the Google GenAI library

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


# --- Chatbot API View ---
@csrf_exempt # Use proper token auth in production if needed
@require_POST
def chatbot_api(request):
    """
    Handles chatbot interaction requests.
    Expects a JSON body with a 'message' key.
    Returns a JSON response with a 'reply' key.
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message')

        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)

        # --- Google Gemini API Call ---
        # IMPORTANT: Get API key securely (e.g., from environment variables)
        api_key = os.environ.get('GOOGLE_API_KEY') # Use GOOGLE_API_KEY
        if not api_key:
            # Return a specific message if the key is missing
            return JsonResponse({'reply': 'Chatbot functionality is not configured (API key missing). Please contact support.'})

        try:
            genai.configure(api_key=api_key)

            # Choose the Gemini model
            model = genai.GenerativeModel('gemini-1.5-flash') # Or another suitable model like 'gemini-pro'

            # Define generation config (optional, adjust as needed)
            generation_config = genai.types.GenerationConfig(
                # temperature=0.7, # Controls randomness
                max_output_tokens=250 # Limit response length
            )

            # Define safety settings (optional, adjust as needed)
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]

            # System prompt - Updated for direct university suggestions
            system_prompt = (
                "You are a university recommendation assistant for the Global Universities platform. "
                "Your primary goal is to suggest universities based on criteria mentioned by the user (e.g., GPA, country, field of study, test scores). "
                "If the user provides criteria like 'GPA 3.4', immediately list potential universities that match, even if the information is limited. "
                "Avoid asking follow-up questions unless the user's request is completely unclear or ambiguous. "
                "Be direct and focus on providing university names or program suggestions based on the input. "
                "If no criteria are provided, you can answer general questions about studying abroad."
            )

            # Start chat (you might want to manage chat history for context)
            # For simplicity here, we start a new chat for each request.
            # Consider storing chat history in the user session or database for longer conversations.
            chat = model.start_chat(history=[
                {'role': 'user', 'parts': [system_prompt]},
                {'role': 'model', 'parts': ["Okay, I understand. How can I help?"]} # Initial model response to system prompt
            ])

            # Send the user's message
            response = chat.send_message(
                user_message,
                generation_config=generation_config,
                safety_settings=safety_settings
            )

            # Extract the text reply
            bot_reply = response.text.strip()

            return JsonResponse({'reply': bot_reply})

        except ValueError as ve:
             # Handle potential configuration or API key errors from genai.configure
             print(f"Gemini Configuration Error: {ve}")
             return JsonResponse({'reply': 'Chatbot configuration error. Please contact support.'})
        except Exception as e:
            # Catch other potential errors from the API call (e.g., network issues, blocked content)
            print(f"Gemini API Error: {e}") # Log the error for debugging
            # Provide a generic error message to the user
            # Check if the error response has specific details about blocking
            if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback'):
                 return JsonResponse({'reply': 'My response was blocked due to safety settings. Please rephrase your question.'})
            return JsonResponse({'reply': 'Sorry, I encountered an error processing your request. Please try again later.'}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        # Catch unexpected errors outside the API call block
        print(f"Chatbot View General Error: {e}")
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)
