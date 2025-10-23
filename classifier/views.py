from django.shortcuts import render
from django.http import JsonResponse
from PIL import Image
from io import BytesIO
from classifier.ml_models.predict import predict  # import your function
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def predict_view(request):
    if request.method == "POST" and "image" in request.FILES:
        uploaded_file = request.FILES["image"]  # InMemoryUploadedFile
        img = Image.open(uploaded_file).convert("RGB")

        top_preds = predict(img, top_k=3)

        return JsonResponse({"predictions": top_preds})

    return JsonResponse({"error": "No image uploaded"}, status=400)