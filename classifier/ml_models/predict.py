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
# Group fruits
# -----------------------------
GROUPS = {
    "apple": ["Fresh Apple(s)", "Rotten Apple(s)"],
    "banana": ["Fresh Banana(s)", "Rotten Banana(s)"],
    "bittergourd": ["Fresh Bittergroud(s)", "Rotten Bittergroud(s)"],
    "capsicum": ["Fresh Capsicum(s)", "Rotten Capsicum(s)"],
    "cucumber": ["Fresh Cucumber(s)", "Rotten Cucumber(s)"],
    "okra": ["Fresh Okra(s)", "Rotten Okra(s)"],
    "orange": ["Fresh Orange(s)", "Rotten Orange(s)"],
    "potato": ["Fresh Potato(s)", "Rotten Potato(s)"],
    "tomato": ["Fresh Tomato(s)", "Rotten Tomato(s)"],
}

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

# -----------------------------
# Segmented prediction function
# -----------------------------
def segmented_predict(img: Image.Image, selected_label: str):
    """
    img: PIL Image
    selected_label: produce selection input 
    conf_threshold: required confidence level to approve input
    returns: list of dicts with keys 'produce', 'produce_confidence', and 'freshness_predictions'
    """
    # Get the fresh and rotten class names for this produce
    fresh_class, rotten_class = GROUPS[selected_label]
    
    # Preprocess and run inference
    inputs = preprocess(img).unsqueeze(0).to(DEVICE)
    
    with torch.no_grad():
        outputs = model(inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=1)
    
    # Convert to CPU for processing
    probs = probs.squeeze(0).cpu()
    
    # Find indices for fresh and rotten classes
    fresh_idx = None
    rotten_idx = None
    
    for idx, label in model.config.id2label.items():
        if label == fresh_class:
            fresh_idx = idx
        elif label == rotten_class:
            rotten_idx = idx
    
    # Handle case where classes aren't found
    if fresh_idx is None or rotten_idx is None:
        raise ValueError(f"Could not find fresh/rotten classes for {selected_label}")
    
    # Get probabilities
    fresh_prob = probs[fresh_idx].item()
    rotten_prob = probs[rotten_idx].item()
    
    # Calculate freshness score (0-100)
    freshness_score = fresh_prob * 100
    
    # Determine status
    status = "Fresh" if fresh_prob > rotten_prob else "Rotten"
    
    return {
        "produce_type": selected_label,
        "fresh_prob": fresh_prob,
        "rotten_prob": rotten_prob,
        "freshness_score": round(freshness_score, 2),
        "status": status
    }