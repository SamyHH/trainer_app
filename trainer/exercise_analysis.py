import math
import cv2
import mediapipe as mp
import numpy as np
from mediapipe.framework.formats.landmark_pb2 import Landmark, LandmarkList
from tensorflow.keras.models import load_model
from trainer.repetition_counter import RepetitionCounter


class ExerciseAnalyzer:
    """
    A class to analyze body exercises using MediaPipe Pose and deep learning models.

    This class provides functionality for:
    - Real-time body pose estimation and feedback.
    - Calculating errors between actual and predicted poses.
    - Displaying visual feedback for exercise form correction.
    - Managing exercise-specific data such as landmarks and models.

    Attributes:
        sequence_length (int): Number of frames to analyze for prediction.
        error_threshold (float): Threshold for significant landmark errors.
        draw_predicted_lm (bool): Whether to draw predicted landmarks on frames.
        visibility_threshold (float): Minimum visibility score for a landmark to be considered visible.
        current_sequence (list): A buffer storing landmark data for sequence-based analysis.
        error_indices (list): Indices of landmarks with significant errors.
        exercise_data (dict): Data about the exercise being analyzed.
        landmark_idx (list): Indices of landmarks used in the current exercise.
        connections_idx (list): Connections between landmarks for drawing.
        model (object): Loaded predictive model for the exercise.
        index_mapping (dict): Mapping from original to reindexed landmark indices.
        mp_pose (object): MediaPipe Pose solution.
        pose (object): Initialized MediaPipe Pose model.
    """
    def __init__(self,
                 exercise_id=1,
                 sequence_length=10,
                 error_threshold=0.1,
                 draw_predicted_lm=True,
                 visibility_threshold=0.5):
        """
        Initialize the ExerciseAnalyzer class with exercise-specific parameters.

        Args:
            exercise_id (int): ID of the exercise to load. Default is 1.
            sequence_length (int): Number of frames for sequence-based prediction. Default is 10.
            error_threshold (float): Threshold for identifying significant errors. Default is 0.1.
            draw_predicted_lm (bool): Whether to draw predicted landmarks on frames. Default is True.
            visibility_threshold (float): Minimum visibility score for a landmark to be considered visible. Default is 0.5.
        """
        self.exercise_id = exercise_id
        self.sequence_length = sequence_length
        self.error_threshold = error_threshold
        self.draw_predicted_lm = draw_predicted_lm
        self.visibibility_threshold = visibility_threshold
        self.current_sequence = []
        self.error_indices = []

        # Load exercise-specific data
        self.exercise_data = self.get_exercise_data()
        self.landmark_idx = self.exercise_data['Landmarks']
        self.connections_idx = self.exercise_data['Connections']
        self.model = self.exercise_data['Model']
        self.index_mapping = self.exercise_data['IndexMapping']

        # Initialize Mediapipe Pose solution
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=False,
                                      model_complexity=1,
                                      smooth_landmarks=True,
                                      enable_segmentation=False,
                                      min_detection_confidence=0.5,
                                      min_tracking_confidence=0.5)

    @staticmethod
    def calculate_distance(point1, point2):
        """
        Calculate the Euclidean distance between two 3D points.

        Args:
            point1 (list or tuple): Coordinates of the first point (x, y, z).
            point2 (list or tuple): Coordinates of the second point (x, y, z).

        Returns:
            float: The Euclidean distance between point1 and point2.
        """
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)


    def are_all_landmarks_visible(self, world_landmarks):
        """
        Check if all specified landmarks are visible above the visibility threshold.

        Args:
            world_landmarks (list): List of landmarks with visibility scores.

        Returns:
            bool: True if all landmarks are visible, False otherwise.
        """
        for idx in self.landmark_idx:
            if world_landmarks[idx].visibility < self.visibibility_threshold:
                return False
        return True


    def get_frame_data(self, world_landmarks):
        """
        Extract 3D coordinates (x, y, z) of specified landmarks.

        Args:
            world_landmarks (list): List of landmarks from pose estimation.

        Returns:
            list: A flat list of 3D coordinates of specified landmarks.
        """
        frame_data = []
        for idx in self.landmark_idx:
            landmark = world_landmarks[idx]
            frame_data.extend([landmark.x, landmark.y, landmark.z])
        return frame_data


    def calculate_errors(self, world_landmarks, predicted_frame):
        """
        Calculate errors between actual and predicted landmark coordinates.

        Args:
            world_landmarks (list): Actual landmarks from pose estimation.
            predicted_frame (list): Predicted coordinates for landmarks.

        Returns:
            tuple: A tuple containing:
                - list: Errors for each landmark.
                - list: Indices of landmarks with errors exceeding the threshold.
        """
        errors = []
        error_indices = []
        for i, idx in enumerate(self.landmark_idx):
            actual_coords = [world_landmarks[idx].x, world_landmarks[idx].y, world_landmarks[idx].z]
            predicted_coords = predicted_frame[i*3:(i+1)*3]

            if len(predicted_coords) == 3:
                distance = self.calculate_distance(actual_coords, predicted_coords)
                errors.append(distance)

                if distance > self.error_threshold:
                    error_indices.append(idx)
        return errors, error_indices


    def display_feedback(self, frame, errors, counter):
        """
        Display feedback on the video frame based on landmark errors.

        Args:
            frame (ndarray): Current video frame.
            errors (list): List of errors for landmarks.
            counter: Repetition Counter

        Feedback includes:
            - Performance score based on mean absolute error (MAE).
            - Repetition Counter
        """

        # Define the rectangle's top-right position
        height, width, _ = frame.shape  # Get dimensions of the image
        top_right_x = width - 250  # Adjust width to place the rectangle in the top-right corner
        top_right_y = 0  # Y-coordinate remains at the top

        # Draw the rectangle in the top-right corner
        cv2.rectangle(frame, (top_right_x, top_right_y), (width, 73), (255, 255, 255), -1)

        # Score
        mae = np.mean(errors) if errors else 0
        if mae:
            performance_score = 100 * (1 - 15 * mae**2)
        else:
            performance_score = 100

        cv2.putText(frame, 'SCORE', (top_right_x + 110,top_right_y+20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(frame, f"{int(performance_score)}%",
                    (top_right_x + 110,top_right_y + 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 2, cv2.LINE_AA)

        # Rep Counter
        cv2.putText(frame, 'REPS', (top_right_x,top_right_y+20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(frame, str(counter),
                    (top_right_x,top_right_y + 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 2, cv2.LINE_AA)

    def draw_landmarks(self, frame, results):
        """
        Draw specified landmarks and their connections on a video frame.

        Args:
            frame (ndarray): The video frame to annotate.
            results (object): Pose estimation results containing landmarks.
        """
        # Initialize Mediapipe drawing utilities
        mp_drawing = mp.solutions.drawing_utils

        # Prepare a list for the landmarks
        filtered_landmarks = []

        # Only include specified landmarks
        for idx in self.landmark_idx:
            landmark = results.pose_landmarks.landmark[idx]

            # Create a Landmark object and append it to the list
            landmark_object = Landmark(
                x=landmark.x,
                y=landmark.y,
                z=landmark.z
            )
            filtered_landmarks.append(landmark_object)

        # Create Landmark List
        landmark_list = LandmarkList(landmark=filtered_landmarks)

        # Define drawing specs for correct and incorrect landmarks
        default_landmark_spec = mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=1)
        correct_landmark_spec = mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=1)
        incorrect_landmark_spec = mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=1)

        # Create a custom dictionary for connection styles
        connection_styles = {}
        for connection in self.connections_idx:
            connection_styles[connection] = correct_landmark_spec
            for idx in self.error_indices:
                if self.index_mapping[idx] in connection:
                    connection_styles[connection] = incorrect_landmark_spec

        # Draw only selected landmarks with appropriate colors
        mp_drawing.draw_landmarks(
            frame,
            landmark_list,  # the standard unfiltered list is -> results.pose_landmarks,
            connections=self.connections_idx,  # Draw only connections specific to the landmarks
            landmark_drawing_spec=default_landmark_spec,  # Default color, customized per landmark
            connection_drawing_spec=connection_styles
        )


    def get_reindexed_connections(self, landmark_idx):
        """
        Generate a list of reindexed connections for the specified landmarks.

        Returns:
            list: Reindexed connections as tuples (start, end).
        """
        mp_pose = mp.solutions.pose
        pose_connections = list(mp_pose.POSE_CONNECTIONS)

        # Create a mapping from the original indices to new indices (re-indexing)
        new_index_mapping = {landmark_idx[i]: i for i in range(len(landmark_idx))}

        # Filter connections that only involve landmarks in the given indices
        filtered_connections = [
            (new_index_mapping[start], new_index_mapping[end])
            for (start, end) in pose_connections
            if start in landmark_idx and end in landmark_idx
        ]

        return filtered_connections

    def get_exercise_data(self):
        """
        Retrieve exercise-specific data, including landmarks, connections, and models.

        Returns:
            dict: A dictionary containing exercise-related information such as landmarks, connections, and models.
        """
        exercise_list = {
            1: {
                'Name': 'Barbell Biceps Curl',
                'Landmarks': [11, 12, 13, 14, 15, 16, 23, 24],
                'ModelID': "barbell_biceps_curl",
                'Min_Threshold': -0.15,
                'Max_Threshold': -0.3
            },
            2: {
                'Name': 'Squats',
                'Landmarks': [11, 12, 23, 24, 25, 26, 27, 28],
                'ModelID': "squats",
                'Min_Threshold': 0.6,
                'Max_Threshold': 0.6
            },
            3: {
                'Name': 'Deadlift',
                'Landmarks': [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28],
                'ModelID': "deadlift",
                'Min_Threshold': 0.6,
                'Max_Threshold': 0.6
            }
        }

        exercise_data = exercise_list.get(self.exercise_id)

        if exercise_data:
            # Get Connections
            exercise_data['Connections'] = self.get_reindexed_connections(exercise_data['Landmarks'])

            # Create a dictionary to map from landmark index to new index
            new_index_list = list(range(len(exercise_data['Landmarks'])))
            exercise_data['IndexMapping'] = {exercise_data['Landmarks'][i]: new_index_list[i] for i in range(len(exercise_data['Landmarks']))}

            # Load the model only when this function is called
            model_path = f"model/{exercise_data['ModelID']}.keras"
            try:
                model = load_model(model_path)
                exercise_data['Model'] = model
            except Exception as e:
                print(f"Error loading model from {model_path}: {e}")
                exercise_data['Model'] = None

        return exercise_data

    def create_predicted_landmarks(self, landmarks, world_landmarks, y_predict):
        """
        Create new landmarks using predicted coordinates.

        Args:
            landmarks (LandmarkList): Original landmarks.
            world_landmarks (LandmarkList): Original world landmarks.
            y_predict (array): Predicted coordinates from the model.

        Returns:
            LandmarkList: A new set of predicted landmarks.
        """
        # Create a new LandmarkList object for the predicted landmarks
        predicted_landmarks = LandmarkList()

        # Loop through the given landmark indices and create new landmarks
        for i, idx in enumerate(self.landmark_idx):
            # Extract corresponding predicted coordinates
            predicted_coords = y_predict[i * 3: (i + 1) * 3]
            actual_coords = [landmarks[idx].x, landmarks[idx].y, landmarks[idx].z]
            world_coords = [world_landmarks[idx].x, world_landmarks[idx].y, world_landmarks[idx].z]

            # Create a new Landmark object for the predicted pose
            predicted_landmark = Landmark()

            # Calculate the direction vector from world to predicted coordinates
            direction_vector = predicted_coords - world_coords

            # Scale this vector to be added to actual_coords, optionally apply a scaling factor
            predicted_landmark_coords = actual_coords + direction_vector

            # Set the predicted values for each coordinate
            predicted_landmark.x = predicted_landmark_coords[0]
            predicted_landmark.y = predicted_landmark_coords[1]
            predicted_landmark.z = predicted_landmark_coords[2]

            # Append the new predicted landmark to the predicted_landmarks list
            predicted_landmarks.landmark.append(predicted_landmark)

        return predicted_landmarks


    def draw_predicted_landmarks(self, frame, results, y_predict):
        """
        Draw predicted landmarks on the video frame.

        Args:
            frame (ndarray): The video frame to annotate.
            results (object): Pose estimation results containing landmarks.
            y_predict (array): Predicted coordinates from the model.
        """

        # Get Landmarks and World Landmarks
        landmarks = results.pose_landmarks.landmark
        world_landmarks = results.pose_world_landmarks.landmark

        # Initialize Mediapipe drawing utilities
        mp_drawing = mp.solutions.drawing_utils

        # Create the predicted landmarks using the provided function
        predicted_landmarks = self.create_predicted_landmarks(landmarks, world_landmarks, y_predict)

        # Define drawing specs for predicted landmarks
        predicted_landmark_spec = mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1, circle_radius=2)
        predicted_connection_spec = mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1)

        # Draw the predicted landmarks on the frame
        mp_drawing.draw_landmarks(
            frame,
            predicted_landmarks,  # The newly created predicted landmarks list
            self.connections_idx,      # Draw only connections specific to the landmarks
            landmark_drawing_spec=predicted_landmark_spec,  # Drawing specs for landmarks
            connection_drawing_spec=predicted_connection_spec  # Drawing specs for connections
        )


    def start_exercise(self, stframe):
        """
        Start an interactive exercise session using a webcam.

        Args:
            stframe (Streamlit Frame): The Streamlit frame for displaying video.

        Process:
            - Captures video using OpenCV.
            - Performs pose estimation with MediaPipe.
            - Compares detected landmarks with predictions.
            - Displays feedback and draws landmarks on the video.
        """

        # Create Repition Counter
        rep_counter = RepetitionCounter(
            landmark_idx=15,
            min_threshold=self.exercise_data['Min_Threshold'],
            max_threshold=self.exercise_data['Max_Threshold'],
            direction_axis='y')

        cap = cv2.VideoCapture(0)

        while cap.isOpened():

            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)  # Flip around the vertical axis
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(frame_rgb)

            # Display Exercise Name
            cv2.putText(frame, f"{self.exercise_data['Name']}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            if results.pose_world_landmarks:
                world_landmarks = results.pose_world_landmarks.landmark

                if self.are_all_landmarks_visible(world_landmarks):
                    frame_data = self.get_frame_data(world_landmarks)
                    self.current_sequence.append(frame_data)

                    if len(self.current_sequence) == self.sequence_length:
                        sequence_array = np.expand_dims(np.array(self.current_sequence), axis=0).astype(np.float32)
                        predicted_frame = self.model.predict(sequence_array, verbose=0)[0]

                        self.current_sequence.pop(0)
                        # Update Counter
                        rep_counter.update(world_landmarks)
                        # Calculate Error
                        errors, self.error_indices = self.calculate_errors(world_landmarks, predicted_frame)
                        # Show Feedback to the User
                        self.display_feedback(frame, errors, counter=rep_counter.get_count())
                        # Draw predicted Landmarks
                        if self.draw_predicted_lm:
                            self.draw_predicted_landmarks(frame, results, predicted_frame)
                else:
                    cv2.putText(frame, "Adjust Position, joints not visible", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            if results.pose_landmarks:
                self.draw_landmarks(frame, results)

            # Convert frame to RGB for displaying with Streamlit
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Display the frame in the Streamlit app
            stframe.image(frame, channels='RGB', use_container_width=True),
