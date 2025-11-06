from django.shortcuts import render
from django.http import JsonResponse
from PIL import Image
from io import BytesIO
from classifier.ml_models.predict import predict, segmented_predict, GROUPS  # import your function
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def predict_view(request):
    if request.method == "POST" and "image" in request.FILES:
        uploaded_file = request.FILES["image"]  # InMemoryUploadedFile
        img = Image.open(uploaded_file).convert("RGB")

        # Get top 3 predictions
        top_preds = predict(img, top_k=3)

        # If user selected a produce type, get segmented prediction
        selected_produce = request.POST.get('produce_type')
        segmented_result = None

        if selected_produce and selected_produce in GROUPS:
            segmented_result = segmented_predict(img, selected_produce)
        
        return JsonResponse({
            "predictions": top_preds,
            "segmented_result": segmented_result,
            "available_produce": list(GROUPS.keys())
        })
    
    return JsonResponse({"error": "No image uploaded"}, status=400)