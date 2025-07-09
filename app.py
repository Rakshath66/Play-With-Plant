import streamlit as st
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

# --- Page Setup ---
st.set_page_config(page_title="🌱 AI Mood Plant", layout="centered")
st.title("🌱 AI Mood Plant")
st.markdown("📸 Click the button to capture emotion, then see how your plant feels!")

@st.cache_resource
def load_emotion_model():
    processor = AutoImageProcessor.from_pretrained("trpakov/vit-face-expression")
    model = AutoModelForImageClassification.from_pretrained("trpakov/vit-face-expression")
    return processor, model

processor, model = load_emotion_model()

# Mood mapping
mood_map = {
    "happy": "Happy", "neutral": "Neutral", "sad": "Sad",
    "angry": "Sad", "disgust": "Sad", "fear": "Sad", "surprise": "Happy"
}
plant_images = {
    "Happy": "plants/happy.jpg",
    "Neutral": "plants/neutral.jpg",
    "Sad": "plants/sad.jpg"
}

# --- UI State ---
if "show_camera" not in st.session_state:
    st.session_state.show_camera = False

# --- Plant placeholder ---
plant_placeholder = st.empty()
plant_placeholder.image(plant_images["Neutral"], caption="🌿 Plant feels: Neutral", width=300)

# --- Buttons ---
col1, col2 = st.columns(2)
if col1.button("📸 Capture Emotion"):
    st.session_state.show_camera = True
if col2.button("❌ Clear Captured Emotion"):
    st.session_state.show_camera = False

# --- Camera Input ---
if st.session_state.show_camera:
    uploaded_file = st.camera_input("")

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1)
            label_id = torch.argmax(probs, dim=1).item()
            raw_emotion = model.config.id2label[label_id].lower()
        mood = mood_map.get(raw_emotion, "Neutral")

        # Update plant and display image
        plant_placeholder.image(plant_images[mood], caption=f"🌿 Plant feels: {mood}", width=300)
        st.image(image, caption="Your captured image", use_container_width=True)
