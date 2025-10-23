import torch
from transformers import AutoModelForImageClassification
from PIL import Image
from torchvision import transforms

# -----------------------------
# Paths / HF model
# -----------------------------
HF_MODEL_REPO = "dbui836/fruitLens"  # your model repo or local folder

# -----------------------------
# Device
# -----------------------------
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -----------------------------
# Load model
# -----------------------------
model = AutoModelForImageClassification.from_pretrained(
    HF_MODEL_REPO, use_safetensors=True
)
model.to(DEVICE)
model.eval()

# -----------------------------
# Image preprocessing
# -----------------------------
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),  # match your training image size
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],  # standard ImageNet stats
                         std=[0.229, 0.224, 0.225])
])

# -----------------------------
# Prediction function
# -----------------------------
def predict(img: Image.Image, top_k: int = 3):
    """
    img: PIL Image
    top_k: number of top predictions to return
    returns: list of dicts with keys 'label' and 'prob'
    """
    inputs = preprocess(img).unsqueeze(0).to(DEVICE)  # add batch dimension

    with torch.no_grad():
        outputs = model(inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=1)

    top_probs, top_indices = torch.topk(probs, top_k)
    top_probs = top_probs.squeeze(0).cpu().tolist()
    top_indices = top_indices.squeeze(0).cpu().tolist()

    top_predictions = [
        {"label": model.config.id2label[idx], "prob": prob}
        for idx, prob in zip(top_indices, top_probs)
    ]

    return top_predictions
