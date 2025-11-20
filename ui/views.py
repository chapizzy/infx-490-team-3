from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Image as ImageModel, Feedback

def get_instruction_popup_state(request):
    if request.user.is_authenticated:
        hide = not request.user.profile.show_instruction_popup
    else:
        hide = request.session.get('hide_instruction_popup', False)
    return JsonResponse({'hide': hide})


# Home page view
def home(request):
    # Determine whether to show the instruction popup
    if request.user.is_authenticated:
        show_popup = getattr(request.user.profile, 'show_instruction_popup', True)
    else:
        show_popup = not request.session.get('hide_instruction_popup', False)
 

    return render(request, "ui/home.html", {"show_popup": show_popup})


# AJAX endpoint to toggle "Don't show again"
@csrf_exempt
def hide_instruction_popup(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        hide = bool(data.get('hide', True))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if request.user.is_authenticated:
        # Logged-in: update profile
        profile = getattr(request.user, 'profile', None)
        if profile:
            profile.show_instruction_popup = not hide
            profile.save()
    else:
        # Anonymous: store in session
        request.session['hide_instruction_popup'] = hide

    return JsonResponse({'success': True})

# What is FoodLens page view
def what_is_foodlens(request):
    return render(request, "ui/what_is_foodlens.html")


# Existing feedback view remains unchanged
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
