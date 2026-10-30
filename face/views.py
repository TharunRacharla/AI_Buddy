import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .slm import ChatGenerationError, generate_reply


@require_POST
def chat(request):
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Request body must be valid JSON."}, status=400)

    if not isinstance(body, dict):
        return JsonResponse({"error": "Request body must be a JSON object."}, status=400)

    user_message = body.get("message")
    if not isinstance(user_message, str) or not user_message.strip():
        return JsonResponse({"error": "A non-empty message is required."}, status=400)
    if len(user_message) > 500:
        return JsonResponse({"error": "Message must be 500 characters or fewer."}, status=400)

    try:
        reply = generate_reply(user_message)
    except ChatGenerationError:
        return JsonResponse(
            {"error": "The assistant could not generate a response. Please try again."},
            status=503,
        )

    return JsonResponse({"reply": reply, "tool_used": None})
