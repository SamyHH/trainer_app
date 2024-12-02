import streamlit as st
from trainer.exercise_analysis import ExerciseAnalyzer
from trainer.utils import process_uploaded_video
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from utils import VideoProcessor
import streamlit as st
from io import BytesIO
from st_on_hover_tabs import on_hover_tabs


exercise_mapping = {
    "Curl Bicep": 1,
    "Squat": 2,
    "Deadlift": 3
}


# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "main"

# Define navigation function
def navigate(page):
    st.session_state.page = page

# Initialize session state
#if 'page' not in st.session_state:
#    st.session_state.page = "main"

# Main Page
if st.session_state.page == "main":
    st.markdown("""
        <style>
            body {
                background-color: black;
            }
            h1 {
                text-align: center;
                margin-top: 50px;
                font-size: 3em;
            }
            p {
                text-align: center;
                font-size: 1.2em;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='color: black;font-size: 100px;'>Tr_AI_Ner</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #ff4b4b;font-size: 60px;text-align: center;'>fitness AI coach</h2>", unsafe_allow_html=True)
    st.image("images/image1_logo.png", use_container_width=True)
    st.markdown("""
        <p style="margin-bottom: 40px; font-size: 24px;"">
            Transform your workouts with Tr_AI_ner Fitness AI Coach, the ultimate web application for personalized fitness guidance. Powered by advanced technology, the app:
        </p>
        <p style="margin-bottom: 20px;font-size: 24px;"">
            Recognizes Exercises
        </p>
        <p style="margin-bottom: 20px;font-size: 24px;"">
            Counts Repetitions
        </p>
        <p style="margin-bottom: 40px;font-size: 24px;"">
            Offers Real-Time Feedback
        </p>
        <p style="margin-bottom: 40px; font-size: 24px;"">
            Achieve your fitness goals safely and efficiently, while minimizing injury risks and maximizing your results
        </p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.7, 1, 1.5])  # Create columns
    with col2:  # Place button in the middle column
        st.button("Get started", on_click=lambda: navigate("second"), type="primary")

# Second Page
elif st.session_state.page == "second":
    st.markdown("""
        <style>
            body {
                background-color: grey;
            }
            .image-container {
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
                padding: 20px;
            }
            .image-block {
                text-align: center;
                margin: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;font-size: 60px;'>Select your exercise</h1>", unsafe_allow_html=True)
    images = ["images/image2_curl.png", "images/image3_squat.png","images/image7_dead.png", "images/image4_jump.png", "images/image5_plank.png", "images/image6_push.png"]
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
            st.image(img, use_container_width=True)

            # Add subcolumns for spacing
            subcols = st.columns([0.6, 1.4])  # Adjust ratio for alignment
            with subcols[1]:  # Right-aligned subcolumn
                exercise_name = button_names[i]
                # Fetch exercise ID from the exercise_mapping
                selected_exercise_id = exercise_mapping.get(exercise_name)

                # Streamlit button for functionality (hidden behind custom button)
                if st.button(exercise_name, type="primary"):
                    if selected_exercise_id:
                        # Store selected exercise id in session state
                        st.session_state.selected_exercise_id = selected_exercise_id
                        # Navigate based on exercise ID
                        if selected_exercise_id == 1:
                            navigate("third")  # Curl Bicep
                        elif selected_exercise_id == 2:
                            navigate("fourth")  # Squat
                        elif selected_exercise_id == 3:
                            navigate("fifth")  # Deadlift


                # Streamlit button for functionality (hidden behind custom button)
                #button_action = None
                #if st.button(button_names[i], type="primary"):
                #    if button_names[i] == "Curl Bicep":
                #        button_action = "third"
                #    elif button_names[i] == "Squat":
                #        button_action = "fourth"
                #    elif button_names[i] == "Deadlift":
                #        button_action = "fifth"
                #    if button_action:
                #        navigate(button_action)

    st.markdown("<div style='margin-top: 70px;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.5, 1, 1.5])  # Create columns
    with col2:  # Place button in the middle column
        st.button("Back to main page", on_click=lambda: navigate("main"))


# Third Page
elif st.session_state.page == "third":
    st.markdown("""
        <style>
            body {
                background-color: grey;
            }
            .coral-box {
                border: 2px solid coral;
                padding: 5px;
                margin: 10px auto;
                width: 20%;
                text-align: center;
                border-radius: 15px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='black-box' style='background-color: black; padding: 5px; border-radius: 10px;'>
        <p style='color: white; font-size: 40px; text-align: center;'>
            Curl Bicep
        </p>
    </div>
""", unsafe_allow_html=True)
    st.image("images/image2_curl.png", use_container_width=True)
    st.markdown("""
    <style>
        .stInfo {
            color: white;
            background-color: #ff4b4b;
        }
    </style>
""", unsafe_allow_html=True)
    st.info("Please stay in front of the camera", icon=None)
    st.info("Check your performance and follow your Tr_AI_ner advices", icon=None)

    col1, col2, col3 = st.columns([1.4, 1, 1])  # Create columns
    with col2:  # Place button in the middle column
        if st.button("Click to start!", type="primary"):
            navigate("ten")

    st.markdown("<div style='margin-top: 70px;'></div>", unsafe_allow_html=True)

    st.button("Back to exercise selection", on_click=lambda: navigate("second"))


# Fourth page
elif st.session_state.page == "fourth":
    st.markdown("""
        <style>
            body {
                background-color: grey;
            }
            .coral-box {
                border: 2px solid coral;
                padding: 5px;
                margin: 10px auto;
                width: 20%;
                text-align: center;
                border-radius: 15px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='black-box' style='background-color: black; padding: 5px; border-radius: 10px;'>
        <p style='color: white; font-size: 40px; text-align: center;'>
            Squat
        </p>
    </div>
""", unsafe_allow_html=True)
    st.image("images/image3_squat.png", use_container_width=True)
    st.markdown("""
    <style>
        .stInfo {
            color: white;
            background-color: #ff4b4b;
        }
    </style>
""", unsafe_allow_html=True)
    st.info("Please stay in front of the camera", icon=None)
    st.info("Check your performance and follow your Tr_AI_ner advices", icon=None)

    col1, col2, col3 = st.columns([1.4, 1, 1])  # Create columns
    with col2:  # Place button in the middle column
        if st.button("Click to start!", type="primary"):
            navigate("ten")

    st.markdown("<div style='margin-top: 70px;'></div>", unsafe_allow_html=True)

    st.button("Back to exercise selection", on_click=lambda: navigate("second"))


# Five page
elif st.session_state.page == "fifth":
    st.markdown("""
        <style>
            body {
                background-color: grey;
            }
            .coral-box {
                border: 2px solid coral;
                padding: 5px;
                margin: 10px auto;
                width: 20%;
                text-align: center;
                border-radius: 15px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='black-box' style='background-color: black; padding: 5px; border-radius: 10px;'>
        <p style='color: white; font-size: 40px; text-align: center;'>
            Deadlift
        </p>
    </div>
""", unsafe_allow_html=True)
    st.image("images/image7_dead.png", use_container_width=True)
    st.markdown("""
    <style>
        .stInfo {
            color: white;
            background-color: #ff4b4b;
        }
    </style>
""", unsafe_allow_html=True)
    st.info("Please stay in front of the camera", icon=None)
    st.info("Check your performance and follow your Tr_AI_ner advices", icon=None)

    col1, col2, col3 = st.columns([1.4, 1, 1])  # Create columns
    with col2:  # Place button in the middle column
        if st.button("Click to start!", type="primary"):
            navigate("ten")

    st.markdown("<div style='margin-top: 70px;'></div>", unsafe_allow_html=True)

    st.button("Back to exercise selection", on_click=lambda: navigate("second"))


# Ten
elif st.session_state.page == "ten":
    st.markdown("""
        <style>
            body {
                background-color: white;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;font-size: 60px;'>Time to excercise</h1>", unsafe_allow_html=True)

    selected_exercise_id = st.session_state.get('selected_exercise_id')

    if selected_exercise_id:

        input_options = [
        "Webcam",
        "Video Upload"
        ]

        input_selection = st.radio("Choose your input", input_options)


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

    st.markdown("<div style='margin-top: 70px;'></div>", unsafe_allow_html=True)

    st.button("Back to exercise selection", on_click=lambda: navigate("second"))
