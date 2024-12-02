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

input_selection = st.radio("Choose your input", input_options)

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

if input_selection == "Video Upload":
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])
    if uploaded_file:
        if st.button("Process Video"):
            exercise = ExerciseAnalyzer(exercise_id=selected_exercise_id)

            # Read video file into BytesIO
            input_video_bytes = BytesIO(uploaded_file.read())
            input_video_bytes.seek(0)

            # Process the video
            with st.spinner("Processing video..."):
                result = process_uploaded_video(input_video_bytes, exercise)

            # Display the processed video
            if result["success"] and result["processed_video_bytes"]:
                processed_video_bytes = result["processed_video_bytes"]
                print(f"Processed video size: {processed_video_bytes.getbuffer().nbytes} bytes")
                if processed_video_bytes.getbuffer().nbytes > 0:
                    st.success("Processing complete!")
                    processed_video_bytes.seek(0)
                    st.download_button(
                        label="Download Processed Video",
                        data=result["processed_video_bytes"],
                        file_name="processed_video.mp4",
                        mime="video/mp4",
                    )
                else:
                    st.error("Processed video is empty.")
