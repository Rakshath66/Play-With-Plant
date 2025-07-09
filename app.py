import streamlit as st
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

# --- Page Setup ---
st.set_page_config(page_title="🌱 AI Mood Plant", layout="centered")
st.title("🌱 AI Mood Plant")
st.markdown("📸 Click the selfie button, then see how your plant feels!")

# --- Load Pretrained FER Model ---
@st.cache_resource
def load_emotion_model():
    processor = AutoImageProcessor.from_pretrained("trpakov/vit-face-expression")
    model = AutoModelForImageClassification.from_pretrained("trpakov/vit-face-expression")
    return processor, model

processor, model = load_emotion_model()

# --- Map raw emotions to 3 moods ---
mood_map = {
    "happy": "Happy",
    "neutral": "Neutral",
    "sad": "Sad",
    "angry": "Sad",
    "disgust": "Sad",
    "fear": "Sad",
    "surprise": "Happy"
}

# --- Plant images path ---
plant_images = {
    "Happy": "plants/happy.jpg",
    "Neutral": "plants/neutral.jpg",
    "Sad": "plants/sad.jpg"
}

# --- Capture Selfie & Run Emotion Detection ---
uploaded_file = st.camera_input("📸 Take a selfie")

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Your Selfie", use_column_width=True)

    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        label_id = torch.argmax(probs, dim=1).item()
        raw_emotion = model.config.id2label[label_id].lower()

    mood = mood_map.get(raw_emotion, "Neutral")
    st.subheader(f"🧠 Detected Emotion: {raw_emotion.capitalize()}")
    st.image(plant_images[mood], caption=f"🌿 Plant feels: {mood}", width=300)
