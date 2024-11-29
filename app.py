from trainer.exercise_analysis import ExerciseAnalyzer
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration, VideoTransformerBase
import cv2
import av
import streamlit as st
import numpy as np


# Callback Function for Video Frame Processing
def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    # Convert the video frame to a NumPy array
    frame = frame.to_ndarray(format="bgr24")
    print

    # Flip the frame horizontally for natural webcam behavior
    frame = cv2.flip(frame, 1)

    # Process the frame using ExerciseAnalyzer
    processed_frame = exercise_analyzer.start_exercise(frame)

    # Return the processed frame
    return av.VideoFrame.from_ndarray(processed_frame, format="bgr24")

class VideoProcessor(VideoTransformerBase):
    def __init__(self, exercise_id):
        self.exercise = ExerciseAnalyzer(exercise_id=exercise_id)

    def transform(self, frame):
        print("Received a frame")  # Debugging
        frame = frame.to_ndarray(format="bgr24")
        print("Frame converted to NumPy array")  # Debugging
        frame = cv2.flip(frame, 1)
        print("Frame flipped")  # Debugging
        # Bypass exercise processing temporarily
        # processed_frame = self.exercise.start_exercise(frame)
        processed_frame = frame  # For debugging, just pass through
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

# Add a button to start or stop the exercise
if 'exercise_started' not in st.session_state:
    st.session_state.exercise_started = False

start_button = st.button('Start/Stop Exercise')

if start_button:
    st.session_state.exercise_started = not st.session_state.exercise_started

if st.session_state.exercise_started:
    # Get the selected exercise ID
    selected_exercise_id = exercise_mapping[exercise_selection]

    # Initialize ExerciseAnalyzer
    exercise_analyzer = ExerciseAnalyzer(exercise_id=selected_exercise_id)

    # WebRTC Configuration
    rtc_configuration = RTCConfiguration({
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}],
        "iceTransportPolicy": "relay",
    })

    # Start the livestream with the selected exercise
    webrtc_streamer(
        key="exercise",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=rtc_configuration,
        #video_frame_callback=video_frame_callback,
        video_processor_factory=lambda: VideoProcessor(exercise_id=selected_exercise_id),
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
else:
    st.write("Press the button to start or stop the exercise.")
