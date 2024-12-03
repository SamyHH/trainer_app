import streamlit as st
from trainer.exercise_analysis import ExerciseAnalyzer
from trainer.utils import process_uploaded_video
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from utils import VideoProcessor
from io import BytesIO

# Get API
api_endpoint = st.secrets["API_ENDPOINT"]

# Initialize session state flags
if "selected_exercise_id" not in st.session_state:
    st.session_state.selected_exercise_id = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "main"

# Exercise mapping
exercise_mapping = {
    "Curl Bicep": 1,
    "Squat": 2,
    "Deadlift": 3
}

# Control which page is visible
def render_page():
    # Main Page
    if st.session_state.current_page == "main":
        render_main_page()

    # Exercise Selection Page
    elif st.session_state.current_page == "exercise_selection":
        render_exercise_selection_page()

    # Exercise Start Page
    elif st.session_state.current_page == "exercise_start":
        render_exercise_start_page()

# Main Page
def render_main_page():
    _, col2, _ = st.columns([0.5, 1, 0.3])  # Adjust column ratios as needed
    with col2:
        st.image("images/image1_logo.png", width=300)

    st.markdown("<h1 style='font-size: 70px;text-align: center'>Tr_AI_Ner</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #ff4b4b;font-size: 50px;text-align: center;'>Fitness AI coach</h2>", unsafe_allow_html=True)

    st.markdown("""
        <p style="font-size: 24px;">
            Transform your workouts with Tr_AI_ner Fitness AI Coach, the ultimate web application for personalized fitness guidance.
        </p>
        <ul style="font-size: 24px;">
            <li>Recognizes Exercises</li>
            <li>Counts Repetitions</li>
            <li>Offers Real-Time Feedback</li>
        </ul>
    """, unsafe_allow_html=True)

    if st.button("Get started"):
        st.session_state.current_page = "exercise_selection"
        st.experimental_rerun()  # Ensures the app immediately navigates

# Exercise Selection Page
def render_exercise_selection_page():
    st.markdown("""
        <style>
            body {
                background-color: grey;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;font-size: 60px;'>Select your exercise</h1>", unsafe_allow_html=True)
    images = [
        "images/image2_curl.png",
        "images/image3_squat.png",
        "images/image7_dead.png",
        "images/image4_jump.png",
        "images/image5_plank.png",
        "images/image6_push.png"
        ]

    button_names = [
        "Curl Bicep",
        "Squat",
        "Deadlift",
        "Jumping jack",
        "Plank",
        "Push up"
        ]  # Define different names for each button

    cols = st.columns(3)
    for i, img in enumerate(images):
        with cols[i % 3]:
            st.image(img)
            if st.button(button_names[i], key=f"exercise_{i}"):
                st.session_state.selected_exercise_id = exercise_mapping[button_names[i]]
                st.session_state.current_page = "exercise_start"
                st.experimental_rerun()

    with st.sidebar:
        st.button("Home", on_click=lambda: setattr(st.session_state, "current_page", "main"))


# Exercise Start Page
def render_exercise_start_page():
    # Display the exercise-specific details
    selected_exercise = st.session_state.selected_exercise_id
    if selected_exercise == 1:
        st.title("Curl Bicep")
        st.image("images/image2_curl.png", width=400)
    elif selected_exercise == 2:
        st.title("Squat")
        st.image("images/image3_squat.png", width=400)
    elif selected_exercise == 3:
        st.title("Deadlift")
        st.image("images/image7_dead.png", width=400)

    st.info("Please stay in front of the camera and follow your Tr_AI_ner's advice.")


    # Sidebar for exercise input options
    with st.sidebar:
        st.button("Exercise Selection", on_click=lambda: setattr(st.session_state, "current_page", "exercise_selection"))

        st.header("Input Options")
        exercise_id = st.session_state.selected_exercise_id

        input_options = ["Webcam", "Video Upload"]
        input_selection = st.radio("Choose your input", input_options)

        # User-configurable options
        st.subheader("Configure Exercise Parameters")

        draw_predicted_lm = st.checkbox(
            "Draw Predicted Landmarks",
            value=True
        )

        error_threshold = st.slider(
            "Error Threshold (tolerance for significant errors)",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.1
        )

        visibility_threshold = st.slider(
            "Visibility Threshold (minimum visibility score for a landmark)",
            min_value=-10.0,
            max_value=10.0,
            value=0.5,
            step=0.1
        )

        sequence_length = st.slider(
            "Sequence Length (number of frames to analyze)",
            min_value=1,
            max_value=30,
            value=10,
            step=1
        )

    if input_selection == "Webcam":
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

        webrtc_streamer(
            key="exercise",
            mode=WebRtcMode.SENDRECV,
            #rtc_configuration=rtc_configuration,
            video_processor_factory=lambda: VideoProcessor(exercise_id=exercise_id,
                                                           draw_predicted_lm=draw_predicted_lm,
                                                           error_threshold=error_threshold,
                                                           visibility_threshold=visibility_threshold,
                                                           api_endpoint=api_endpoint,
                                                           sequence_length=sequence_length
                                                           ),
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
                exercise = ExerciseAnalyzer(exercise_id=exercise_id,
                                            draw_predicted_lm=draw_predicted_lm,
                                            error_threshold=error_threshold,
                                            visibility_threshold=visibility_threshold,
                                            api_endpoint=api_endpoint,
                                            sequence_length=sequence_length
                                            )

                input_video_bytes = BytesIO(uploaded_file.read())
                input_video_bytes.seek(0)

                with st.spinner("Processing video..."):
                    result = process_uploaded_video(input_video_bytes, exercise)

                if result["success"]:
                    st.success("Processing complete!")
                    st.download_button(
                        label="Download Processed Video",
                        data=result["processed_video_bytes"],
                        file_name="processed_video.mp4",
                        mime="video/mp4",
                    )
                else:
                    st.error("Processing failed.")


# Render the appropriate page
render_page()
