from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        user_message = body.get('message', '')

        reply = f"You said: {user_message}"
        tool_used = None  

        return JsonResponse({
            "reply": reply,
            "tool_used": tool_used
        })