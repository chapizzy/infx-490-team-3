from django.http import JsonResponse
from PIL import Image as PILImage
from io import BytesIO
from classifier.ml_models.predict import predict  # import your function
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

        top_preds = predict(img, top_k=3)

        return JsonResponse({"predictions": top_preds, "image_id": image_obj.id})

    return JsonResponse({"error": "No image uploaded"}, status=400)