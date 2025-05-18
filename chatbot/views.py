import os
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Default model, but you can change this to any model OpenRouter supports
DEFAULT_MODEL = "anthropic/claude-3-haiku" # Or another model like "openai/gpt-3.5-turbo", "anthropic/claude-3-opus", etc.

@csrf_exempt  # Use csrf_exempt for simplicity in this example, consider CSRF protection for production
@require_POST
def chat_with_ai(request):
    if not OPENROUTER_API_KEY:
        return JsonResponse({'error': 'OpenRouter API key not configured'}, status=500)

    try:
        data = json.loads(request.body)
        user_message = data.get('message')

        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)

        # Prepare the request to OpenRouter
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv('SITE_URL', 'http://localhost:8000'),  # Optional but good practice
            "X-Title": os.getenv('SITE_TITLE', 'Django Chatbot')  # Optional identifier for your app
        }

        payload = {
            "model": DEFAULT_MODEL,
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }

        # Send request to OpenRouter
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses

        response_data = response.json()
        
        # Extract the AI's reply
        ai_reply = response_data['choices'][0]['message']['content']
        
        return JsonResponse({'reply': ai_reply})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return JsonResponse({'error': 'Rate limit exceeded. Please try again later.'}, status=429)
        return JsonResponse({'error': f'API error: {str(e)}'}, status=e.response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Connection error: {str(e)}'}, status=500)
    except Exception as e:
        print(f"Error during OpenRouter API call: {e}")
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

# You might want to add a simple view to render the chat interface if needed
# from django.shortcuts import render
# def chat_interface(request):
#     return render(request, 'chatbot/chat_interface.html')  # Example template name