import cv2
import os
import uuid
from io import BytesIO
import subprocess

def reencode_video(input_path, output_path):
    try:
        command = [
            "ffmpeg", "-i", input_path,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-pix_fmt", "yuv420p",  # Ensures compatibility
            "-movflags", "+faststart",  # Optimizes for streaming
            output_path
        ]
        subprocess.run(command, check=True)
        print(f"Re-encoding complete: {output_path}")
    except Exception as e:
        print(f"Error during FFMPEG re-encoding: {e}")
        raise


def process_uploaded_video(input_video_bytes, exercise_analyzer):
    """
    Process the uploaded video frame by frame using start_exercise.
    Args:
        input_video_bytes (BytesIO): Input video as a BytesIO object.
        exercise_analyzer (ExerciseAnalyzer): Instance of ExerciseAnalyzer.

    Returns:
        dict: A dictionary containing:
            - 'success' (bool): Whether the video was processed successfully.
            - 'processed_video_bytes' (BytesIO): Processed video as a BytesIO object.
            - 'frames_processed' (int): Number of frames processed.
    """
    processed_video_bytes = BytesIO()
    try:
        # Write input BytesIO to a temporary file for OpenCV compatibility
        input_temp_file = f"/tmp/input_video_{uuid.uuid4().hex}.mp4"
        with open(input_temp_file, "wb") as f:
            f.write(input_video_bytes.read())

        # Open input video
        cap = cv2.VideoCapture(input_temp_file)
        if not cap.isOpened():
            print("Error: Unable to open input video file.")
            return {"success": False, "processed_video_bytes": None, "frames_processed": 0}

        # Video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        # Write to an in-memory file for processed video
        output_temp_file = f"/tmp/output_video_{uuid.uuid4().hex}.mp4"
        out = cv2.VideoWriter(output_temp_file, fourcc, fps, (width, height))
        if not out.isOpened():
            print("Error: Unable to initialize VideoWriter.")
            return {"success": False, "processed_video_bytes": None, "frames_processed": 0}

        # Process frames
        frames_processed = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process frame
            processed_frame = exercise_analyzer.start_exercise(frame)
            processed_frame = cv2.resize(processed_frame, (width, height))
            out.write(processed_frame)
            frames_processed += 1
            print(f"Processed frame {frames_processed}")

        cap.release()
        out.release()

        # Write output file to BytesIO
        with open(output_temp_file, "rb") as f:
            processed_video_bytes.write(f.read())

        # Clean up
        os.remove(input_temp_file)
        os.remove(output_temp_file)

        processed_video_bytes.seek(0)  # Reset BytesIO pointer
        print("Video processing complete.")
        return {"success": True, "processed_video_bytes": processed_video_bytes, "frames_processed": frames_processed}
    except Exception as e:
        print(f"Error processing video: {e}")
        return {"success": False, "processed_video_bytes": None, "frames_processed": 0}

# def process_uploaded_video(input_video_bytes, exercise_analyzer):
#     processed_video_bytes = BytesIO()
#     try:
#         input_temp_file = f"/tmp/input_video_{uuid.uuid4().hex}.mp4"
#         output_temp_file = f"/tmp/output_video_{uuid.uuid4().hex}.mp4"
#         reencoded_temp_file = f"/tmp/reencoded_video_{uuid.uuid4().hex}.mp4"

#         # Write input video to temp file
#         with open(input_temp_file, "wb") as f:
#             f.write(input_video_bytes.read())

#         cap = cv2.VideoCapture(input_temp_file)
#         if not cap.isOpened():
#             print("Error: Unable to open input video file.")
#             return {"success": False, "processed_video_bytes": None, "frames_processed": 0}

#         fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
#         width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#         height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')

#         out = cv2.VideoWriter(output_temp_file, fourcc, fps, (width, height))
#         frames_processed = 0

#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break
#             processed_frame = exercise_analyzer.start_exercise(frame)
#             processed_frame = cv2.resize(processed_frame, (width, height))
#             out.write(processed_frame)
#             frames_processed += 1

#         cap.release()
#         out.release()

#         # Re-encode the processed video
#         reencode_video(output_temp_file, reencoded_temp_file)

#         # Write re-encoded video to BytesIO
#         with open(reencoded_temp_file, "rb") as f:
#             processed_video_bytes.write(f.read())

#         # Clean up temp files
#         os.remove(input_temp_file)
#         os.remove(output_temp_file)
#         os.remove(reencoded_temp_file)

#         processed_video_bytes.seek(0)
#         return {"success": True, "processed_video_bytes": processed_video_bytes, "frames_processed": frames_processed}
#     except Exception as e:
#         print(f"Error processing video: {e}")
#         return {"success": False, "processed_video_bytes": None, "frames_processed": 0}



def process_webcam_video(exercise_analyzer, display_callback, placeholder=None):
    """
    Process the webcam video frame by frame using start_exercise and a dynamic display callback.

    Args:
        exercise_analyzer (ExerciseAnalyzer): The exercise analyzer instance.
        display_callback (callable): A function to handle displaying frames.
        placeholder: Optional Streamlit placeholder for displaying frames.

    Returns:
        dict: A dictionary containing:
            - 'success' (bool): Whether the video stream was processed successfully.
            - 'frames_processed' (int): Number of frames processed.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to open webcam.")
        return {"success": False, "frames_processed": 0}

    frames_processed = 0
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            # Process the frame using start_exercise
            processed_frame = exercise_analyzer.start_exercise(frame)

            # Convert processed frame from BGR to RGB
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

            # Use the provided callback to display the frame
            display_callback(processed_frame, placeholder)
            frames_processed += 1

        return {"success": True, "frames_processed": frames_processed}
    except Exception as e:
        print(f"Error processing webcam video: {e}")
        return {"success": False, "frames_processed": frames_processed}
    finally:
        cap.release()
