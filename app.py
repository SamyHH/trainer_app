from trainer.exercise_analysis import ExerciseAnalyzer
from trainer.utils import process_uploaded_video
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from utils import VideoProcessor
import streamlit as st
from io import BytesIO

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

    # Placeholder for processed video
    processed_video_bytes = BytesIO()

    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])
    if uploaded_file:
        st.video(uploaded_file)

        if st.button("Process Video"):
            exercise = ExerciseAnalyzer(exercise_id=selected_exercise_id)

            # Read the uploaded video into BytesIO
            input_video_bytes = BytesIO(uploaded_file.read())
            input_video_bytes.seek(0)  # Reset pointer

            with st.spinner("Processing video..."):
                # Process the video and write to BytesIO
                result = process_uploaded_video(input_video_bytes, processed_video_bytes, exercise)

            if result["success"]:
                # Display processed video
                processed_video_bytes.seek(0)  # Reset pointer for playback
                st.success("Processing complete!")
                st.video(processed_video_bytes)
            else:
                st.error("Video processing failed.")
