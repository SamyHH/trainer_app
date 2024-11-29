from trainer.exercise_analysis import ExerciseAnalyzer
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration, VideoTransformerBase
import cv2
import av
import streamlit as st

class VideoProcessor(VideoTransformerBase):
    def __init__(self, exercise_id):
        print(f"Initializing VideoProcessor with exercise_id: {exercise_id}")
        self.exercise = ExerciseAnalyzer(exercise_id=exercise_id)

    def recv(self, frame):
        frame = frame.to_ndarray(format="bgr24")
        frame = cv2.flip(frame, 1)
        processed_frame = self.exercise.start_exercise(frame)
        return av.VideoFrame.from_ndarray(processed_frame, format="bgr24")

# Streamlit App Implementation
st.title("Tr_AI_ner")
st.header("Start to check your training!")

# Radio buttons for exercise selection
exercise_options = [
    "Barbell Biceps Curls",
    "Squats",
    "Deadlift"
]
exercise_selection = st.radio("Choose your exercise", exercise_options)

# Map exercise names to their respective IDs
exercise_mapping = {
    "Barbell Biceps Curls": 1,
    "Squats": 2,
    "Deadlift": 3
}

# Get the selected exercise ID
selected_exercise_id = exercise_mapping[exercise_selection]

# WebRTC Configuration
rtc_configuration = RTCConfiguration({
"iceServers": [
    {"urls": ["stun:stun.l.google.com:19302"]},
    {"urls": ["stun:stun1.l.google.com:19302"]},
    {"urls": ["stun:stun2.l.google.com:19302"]},
    {
        "urls": ["turn:relay.metered.ca:80"],
        "username": "user",
        "credential": "password"
    }
],
"iceTransportPolicy": "all",
})

# Start the livestream with the selected exercise
webrtc_streamer(
    key="exercise",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=rtc_configuration,
    video_processor_factory=lambda: VideoProcessor(exercise_id=selected_exercise_id),
    media_stream_constraints={
    "video": {
        "width": {"ideal": 1280},
        "height": {"ideal": 720},
        "frameRate": {"ideal": 30},
        },
    "audio": False,
    },
)
