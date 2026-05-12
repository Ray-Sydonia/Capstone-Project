import numpy as np
from PIL import Image

try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    from tensorflow.keras.applications.resnet50 import preprocess_input
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(BASE_DIR, "..", "hair_damage_resnet50_model.keras")
    model = load_model(model_path)
    TENSORFLOW_AVAILABLE = True
    print("TensorFlow loaded successfully!")
except Exception as e:
    TENSORFLOW_AVAILABLE = False
    model = None
    print(f"TensorFlow error: {type(e).__name__}: {e}")  # ← shows the REAL error

CLASS_NAMES = [
"breakage", 
"chemical_damage",
"dry",
"healthy", 
"heat_damage", 
"split_ends"]

def preprocess_image(image_file):
    img = Image.open(image_file).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img, dtype=np.float32)
    img_array = np.expand_dims(img_array, axis=0)
    return preprocess_input(img_array)  # ✅ matches ResNet50 training

def predict_damage(image_file):
    if not TENSORFLOW_AVAILABLE:
        return {
            "predicted_class": "Unavailable",
            "confidence": 0.0,
            "error": "TensorFlow not installed"
        }
    
    img_input = preprocess_image(image_file)
    prediction = model.predict(img_input)[0]

    # ✅ Add this temporarily
    print("Raw predictions:", prediction)
    print("Class scores:", dict(zip(CLASS_NAMES, prediction)))

    class_index = int(np.argmax(prediction))
    confidence = float(np.max(prediction))

    return {
        "predicted_class": CLASS_NAMES[class_index],
        "confidence": confidence
    }