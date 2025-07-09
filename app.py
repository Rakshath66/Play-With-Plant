import streamlit as st
import tensorflow as tf
import numpy as np
import cv2
import av
import threading
import time
from PIL import Image
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
from keras.layers import TFSMLayer


# ✅ Load model
model = TFSMLayer("converted_savedmodel/model.savedmodel", call_endpoint="serving_default")
with open("converted_savedmodel/labels.txt", "r") as f:
    class_names = [line.strip() for line in f.readlines()]

plant_images = {
    "Happy": "plants/happy.jpg",
    "Neutral": "plants/neutral.jpg",
    "Sad": "plants/sad.jpg"
}

# ✅ Global mood
global_mood = {"value": "Neutral"}
lock = threading.Lock()

# ✅ Prediction logic
def predict_emotion(image_np):
    try:
        normalized = (image_np / 127.5) - 1.0
        data = np.expand_dims(normalized, axis=0).astype(np.float32)

        output = model(data)
        if isinstance(output, dict):
            prediction = next(iter(output.values()))
        else:
            prediction = output

        if hasattr(prediction, "numpy"):
            prediction = prediction.numpy()

        print("Prediction values:", prediction)
        print("Predicted mood:", mood)

        index = np.argmax(prediction)
        mood = class_names[index]


        with lock:
            global_mood["value"] = mood
    except Exception as e:
        print("Prediction error:", e)

# ✅ Video processor
class EmotionDetector(VideoProcessorBase):
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = Image.fromarray(img_rgb).resize((224, 224))
        image_array = np.asarray(img_resized).astype(np.float32)

        threading.Thread(target=predict_emotion, args=(image_array,), daemon=True).start()

        with lock:
            mood = global_mood["value"]
        cv2.putText(img, f"Mood: {mood}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# ✅ Streamlit UI
st.set_page_config(page_title="🌱 AI Mood Plant", layout="centered")
st.title("🌱 AI Mood Plant")
st.markdown("Let your smile grow a plant! Your mood powers the plant's growth 🌿")

# ✅ Start webcam
ctx = webrtc_streamer(
    key="mood-stream",
    video_processor_factory=EmotionDetector,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"video": True, "audio": False}
)

# ✅ Mood plant section
import time

st.subheader("🪴 Your Plant's Mood")

# ⏳ Create placeholder
plant_placeholder = st.empty()

# 💾 Track last displayed mood
if "last_mood" not in st.session_state:
    st.session_state.last_mood = None

# 🔁 Loop only if camera is active
if ctx and ctx.state.playing:
    while True:
        with lock:
            current_mood = global_mood["value"]
            st.text(f"DEBUG: Current mood = {current_mood}")


        # Only update if mood changed
        if current_mood != st.session_state.last_mood:
            st.session_state.last_mood = current_mood
            plant_img = Image.open(plant_images[current_mood])
            plant_placeholder.image(plant_img, width=300, caption=f"The plant feels: {current_mood}")

        time.sleep(1)

