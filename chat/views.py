from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from chat.utils.inference import generate_response
import datetime
import json

def index(request):
    return render(request, 'chat/chat.html')

def chat(request):
    if request.method == 'POST':
        print("here")
        data = json.loads(request.body)
        message = data.get('message', '')
        print(message)
        return JsonResponse({
            'response': generate_response(message),
            'timestamp': datetime.datetime.now().strftime("%I:%M %p"),
        })
    return JsonResponse({'error': 'Invalid request method.'}, status=400)
