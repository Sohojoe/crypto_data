import numpy as np

class StreamingWindow:
    def __init__(self, window_size, num_features=5, dtype=np.float64):
        self.window_size = window_size
        self.num_features = num_features
        self.buffer = np.zeros((num_features, window_size * 2), dtype=dtype)
        self.current_index = 0  # Tracks the current timestep for updates
        self.data_count = 0  # Tracks how many times data has been added

    def add_data(self, data):
        if len(data) != self.num_features:
            raise ValueError(f"Data length must be {self.num_features}")
        
        # Update the buffer with new data
        self.buffer[:, self.current_index] = data
        self.buffer[:, self.current_index + self.window_size] = data
        
        # Increment the current index and data count, wrapping the index as needed
        self.current_index = (self.current_index + 1) % self.window_size
        self.data_count += 1

    def get_current_window(self):
        # Calculate the effective window size based on the amount of data added
        effective_window_size = min(self.data_count, self.window_size)
        
        if self.data_count <= self.window_size:
            return self.buffer[:, :effective_window_size]
        else:
            # Calculate start and end positions for the circular buffer
            start = self.current_index
            end = (start + effective_window_size) % (self.window_size * 2)
            if start < end:
                return self.buffer[:, start:end]
            else:
                return np.hstack((self.buffer[:, start:], self.buffer[:, :end]))
