from trainer.exercise_analysis import ExerciseAnalyzer
from trainer.utils import process_uploaded_video
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from utils import VideoProcessor
import streamlit as st
import tempfile
import os
import uuid


# Streamlit App Implementation
st.title("Tr_AI_ner")
st.header("Start to check your training!")

# Radio buttons for input selection
input_options = [
    "Webcam",
    "Video Upload"
]

input_selection = st.radio("Choose your inout", input_options)

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

if input_selection == "Webcam":
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

elif input_selection == "Video Upload":
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])

    if uploaded_file is not None:
        st.video(uploaded_file)

        if st.button("Process Video"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as input_tempfile:
                input_tempfile.write(uploaded_file.read())
                input_path = input_tempfile.name

            # Unique output file
            output_path = f"/tmp/processed_video_{uuid.uuid4().hex}.mp4"

            exercise = ExerciseAnalyzer(exercise_id=selected_exercise_id)
            # Process the video
            try:
                with st.spinner("Processing video..."):
                    process_uploaded_video(input_path, output_path, exercise)

                # Display Processed Video
                if os.path.exists(output_path):
                    st.success("Processing complete!")
                    st.video(output_path)
                else:
                    st.error("Failed to process video.")
            finally:
                # Clean up temporary input file
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
