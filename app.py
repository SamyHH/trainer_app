from trainer.exercise_analysis import ExerciseAnalyzer
import streamlit as st

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

    # Create an empty space in Streamlit to display the video frames
    stframe = st.empty()

    # Start the selected exercise
    exercise = ExerciseAnalyzer(exercise_id=selected_exercise_id)
    exercise.start_exercise(stframe)
else:
    st.write("Press the button to start or stop the exercise.")
