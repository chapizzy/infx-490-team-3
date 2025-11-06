from django.http import JsonResponse
from PIL import Image as PILImage
from io import BytesIO
from classifier.ml_models.predict import predict, segmented_predict, GROUPS  # import your function
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from ui.models import Image as ImageModel, Produce as ProduceModel

@csrf_exempt
def predict_view(request):
    if request.method == "POST" and "image" in request.FILES:
        uploaded_file = request.FILES["image"]  # InMemoryUploadedFile

        # read bytes so we can both save the file and open with PIL
        data = uploaded_file.read()
        img = PILImage.open(BytesIO(data)).convert("RGB")

        # ensure there's at least one Produce to attach (app expects a produce FK)
        produce, _ = ProduceModel.objects.get_or_create(name='unspecified', defaults={'category': 'unknown'})

        # create and save Image model instance
        image_obj = ImageModel.objects.create(
            produce=produce,
            user=request.user if request.user.is_authenticated else None,
            status='processing'
        )
        # save the uploaded image file into the Image.image_path field
        image_obj.image_path.save(uploaded_file.name, ContentFile(data))
        image_obj.status = 'analyzed'
        image_obj.save()

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