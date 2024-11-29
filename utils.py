from streamlit_webrtc import VideoTransformerBase
from trainer.exercise_analysis import ExerciseAnalyzer
import cv2
import av

def streamlit_display_callback(frame, placeholder):
    """
    A Streamlit-specific callback to display video frames.
    """
    placeholder.image(frame, channels="RGB")

class VideoProcessor(VideoTransformerBase):
    def __init__(self, exercise_id):
        print(f"Initializing VideoProcessor with exercise_id: {exercise_id}")
        self.exercise = ExerciseAnalyzer(exercise_id=exercise_id)

    def recv(self, frame):
        frame = frame.to_ndarray(format="bgr24")
        frame = cv2.flip(frame, 1)
        processed_frame = self.exercise.start_exercise(frame)
        return av.VideoFrame.from_ndarray(processed_frame, format="bgr24")
