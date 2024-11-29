import cv2

def process_uploaded_video(video_path, output_path, exercise_analyzer):
    """
    Process the uploaded video frame by frame using start_exercise.
    Args:
        video_path (str): Path to the input video.
        output_path (str): Path to save the processed video.
        exercise_analyzer (ExerciseAnalyzer): Instance of ExerciseAnalyzer.

    Returns:
        dict: A dictionary containing:
            - 'success' (bool): Whether the video was processed successfully.
            - 'output_path' (str): Path to the processed video file.
            - 'frames_processed' (int): Number of frames processed.
    """
    cap = cv2.VideoCapture(video_path)

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fps = fps if fps > 0 else 30  # Default FPS if invalid
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # Use H.264 codec

    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frames_processed = 0
    try:
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

        print(f"Video processing complete. Output saved to {output_path}")
        return {"success": True, "output_path": output_path, "frames_processed": frames_processed}
    except Exception as e:
        print(f"Error processing video: {e}")
        return {"success": False, "output_path": output_path, "frames_processed": frames_processed}
    finally:
        cap.release()
        out.release()


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
