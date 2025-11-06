from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Home page view
def home(request):
    return render(request, "ui/home.html")


# What is FoodLens page view
def what_is_foodlens(request):
    return render(request, "ui/what_is_foodlens.html")


@csrf_exempt
def submit_feedback(request):
    """Accept JSON POST with {image_id, helpful, explanation} and save Feedback."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    image_id = data.get('image_id')
    helpful = data.get('helpful')
    explanation = data.get('explanation', '')

    # normalize helpful
    if isinstance(helpful, str):
        helpful = helpful.lower() in ('true', '1', 'yes', 'y')

    from .models import Image as ImageModel, Feedback

    try:
        image = ImageModel.objects.get(id=image_id)
    except (ImageModel.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'error': 'Image not found'}, status=404)

    # ensure session exists so we can track anonymous visitors
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    fb = Feedback.objects.create(
        image=image,
        user=request.user if request.user.is_authenticated else None,
        helpful=helpful,
        explanation=explanation,
        session_key=session_key,
    )

    return JsonResponse({'success': True, 'feedback_id': fb.id})