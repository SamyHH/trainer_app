class RepetitionCounter:
    def __init__(self, landmark_idx, direction_axis='y', threshold=0.1, min_threshold=None, max_threshold=None):
        """
        A class to count repetitions based on movement along a specific axis.

        Args:
            landmark_idx (int): The index of the landmark to track.
            direction_axis (str): The axis along which to track movement ('x', 'y', 'z').
            threshold (float): The threshold value to determine significant movement.
            min_threshold (float): The lower threshold for determining the movement bottom.
            max_threshold (float): The upper threshold for determining the movement top.
        """
        self.landmark_idx = landmark_idx
        if min_threshold == None and max_threshold == None:
            self.min_threshold = threshold
            self.max_threshold = threshold
        else:
            self.min_threshold = min_threshold
            self.max_threshold = max_threshold
        self.direction_axis = direction_axis
        self.previous_state = None
        self.counter = 0

    def update(self, landmarks):
        """
        Update counter based on the movement of the given landmark.

        Args:
            landmarks (list): A list of landmark coordinates from the pose.
        """
        if not landmarks or self.landmark_idx >= len(landmarks):
            return

        # Get the coordinate value along the specified axis
        if self.direction_axis == 'y':
            current_value = landmarks[self.landmark_idx].y
        elif self.direction_axis == 'x':
            current_value = landmarks[self.landmark_idx].x
        elif self.direction_axis == 'z':
            current_value = landmarks[self.landmark_idx].z
        else:
            return

        # Track state (e.g., 'up' or 'down') based on y-movement and threshold
        if current_value < self.max_threshold:  # Going down
            if self.previous_state != 'down':
                self.previous_state = 'down'
        elif current_value > self.min_threshold:  # Going up
            if self.previous_state == 'down':
                self.previous_state = 'up'
                self.counter += 1  # Increment repetition count when standing back up

    def get_count(self):
        """
        Get the current count of repetitions.

        Returns:
            int: The number of complete repetitions detected.
        """
        return self.counter
