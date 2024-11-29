from streamlit_webrtc import webrtc_streamer, RTCConfiguration, WebRtcMode, VideoTransformerBase
import streamlit as st
import cv2
import av

class VideoProcessor(VideoTransformerBase):
    def __init__(self):
        super().__init__()
        print("VideoProcessor initialized")  # Debugging

    def transform(self, frame):
        print("Received a frame")  # Debugging
        try:
            frame = frame.to_ndarray(format="bgr24")
            print("Frame converted to NumPy array")  # Debugging
            frame = cv2.flip(frame, 1)
            print("Frame flipped")  # Debugging
            return av.VideoFrame.from_ndarray(frame, format="bgr24")
        except Exception as e:
            print(f"Error processing frame: {e}")
            raise

st.title("WebRTC Debug Test")

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

print("Initializing WebRTC...")
webrtc_streamer(
    key="debug",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=rtc_configuration,
    video_processor_factory=VideoProcessor,
    media_stream_constraints={"video": True, "audio": False},
)
print("WebRTC initialized")
