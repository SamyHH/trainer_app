import cv2
import os
import uuid

def process_uploaded_video(input_video_bytes, output_video_bytes, exercise_analyzer):
    """
    Process the uploaded video frame by frame using start_exercise.
    Args:
        input_video_bytes (BytesIO): Input video as a BytesIO object.
        output_video_bytes (BytesIO): Output video as a BytesIO object.
        exercise_analyzer (ExerciseAnalyzer): Instance of ExerciseAnalyzer.

    Returns:
        dict: A dictionary containing:
            - 'success' (bool): Whether the video was processed successfully.
            - 'frames_processed' (int): Number of frames processed.
    """
    try:
        # Write input BytesIO to a temporary file for OpenCV compatibility
        input_temp_file = f"/tmp/input_video_{uuid.uuid4().hex}.mp4"
        with open(input_temp_file, "wb") as f:
            f.write(input_video_bytes.read())

        cap = cv2.VideoCapture(input_temp_file)

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        fps = fps if fps > 0 else 30  # Default FPS if invalid
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use H.264 codec

        # Open an in-memory VideoWriter
        output_temp_file = f"/tmp/output_video_{uuid.uuid4().hex}.mp4"
        out = cv2.VideoWriter(output_temp_file, fourcc, fps, (width, height))

        frames_processed = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process the frame using start_exercise
            processed_frame = exercise_analyzer.start_exercise(frame)

            # Ensure dimensions match
            processed_frame = cv2.resize(processed_frame, (width, height))

            # Write the processed frame to the output video
            out.write(processed_frame)
            frames_processed += 1

        # Release resources
        cap.release()
        out.release()

        # Write output temp file to BytesIO
        with open(output_temp_file, "rb") as f:
            output_video_bytes.write(f.read())

        # Clean up temporary files
        os.remove(input_temp_file)
        os.remove(output_temp_file)

        print("Video processing complete.")
        return {"success": True, "frames_processed": frames_processed}
    except Exception as e:
        print(f"Error processing video: {e}")
        return {"success": False, "frames_processed": 0}



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
