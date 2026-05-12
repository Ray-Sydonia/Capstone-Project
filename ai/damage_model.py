import os
import numpy as np
from PIL import Image

# ── Safe TensorFlow import ─────────────────────────────────────────────────
# preprocess_input is also part of TensorFlow so it must be inside the try block.
# Moving ALL tf imports here means the file loads cleanly even without TensorFlow.
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    from tensorflow.keras.applications.resnet50 import preprocess_input

    BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(BASE_DIR, "hair_damage_resnet50_multilabel.keras")
    model      = load_model(model_path)

    TENSORFLOW_AVAILABLE = True
    print("TensorFlow loaded successfully!")

except Exception as e:
    TENSORFLOW_AVAILABLE = False
    model = None
    print(f"TensorFlow error: {type(e).__name__}: {e}")

# ── Constants ──────────────────────────────────────────────────────────────
CLASS_NAMES = [
    "breakage",
    "chemical_damage",
    "dry",
    "healthy",
    "heat_damage",
    "split_ends",
]

# Threshold above which a label is considered detected (multilabel).
# Adjust this if the model is over- or under-predicting.
THRESHOLD = 0.5


# ── Preprocessing ──────────────────────────────────────────────────────────
def preprocess_image(image_file):
    """Open an image file-like object and prepare it for ResNet-50."""
    img       = Image.open(image_file).convert("RGB")
    img       = img.resize((224, 224))
    img_array = np.array(img, dtype=np.float32)
    img_array = np.expand_dims(img_array, axis=0)
    return preprocess_input(img_array)   # matches ResNet-50 training normalisation


# ── Prediction ─────────────────────────────────────────────────────────────
def predict_damage(image_file):
    """
    Run the multilabel classifier on image_file.

    Returns a dict:
      {
        "categories":   ["breakage", "dry"],          # labels above THRESHOLD
        "confidences":  {"breakage": 0.91, "dry": 0.73, ...},  # all 6 scores
        "error":        None                           # or an error string
      }

    The frontend (strand-test.html) expects exactly this shape.
    """
    if not TENSORFLOW_AVAILABLE:
        return {
            "categories":  [],
            "confidences": {c: 0.0 for c in CLASS_NAMES},
            "error": "TensorFlow not installed — AI predictions unavailable.",
        }

    img_input  = preprocess_image(image_file)
    prediction = model.predict(img_input)[0]   # shape: (6,)

    # Debug — remove these two lines once the model is confirmed working
    print("Raw predictions:", prediction)
    print("Class scores:",    dict(zip(CLASS_NAMES, prediction)))

    confidences = {CLASS_NAMES[i]: float(prediction[i]) for i in range(len(CLASS_NAMES))}
    categories  = [label for label, score in confidences.items() if score >= THRESHOLD]

    # Fallback: if nothing clears the threshold, take the single highest score
    if not categories:
        best = max(confidences, key=confidences.get)
        categories = [best]

    return {
        "categories":  categories,
        "confidences": confidences,
        "error":       None,
    }