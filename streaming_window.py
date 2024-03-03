import numpy as np

class StreamingWindow:
    def __init__(self, max_window_size, dtype=float):
        self.max_window_size = max_window_size
        self.buffer_size = max_window_size * 2  # Buffer size is twice the window size
        self.dtype = dtype  # Data type for the buffer
        self.buffer = np.zeros(self.buffer_size, dtype=self.dtype)  # Initialize buffer with specified data type
        self.items_added = 0  # Track the number of items added to the buffer

    def add_data(self, new_data):
        # Ensure new_data is of the correct dtype
        new_data = np.asarray(new_data, dtype=self.dtype)
        # Calculate the current position based on items added
        current_position = self.items_added % self.max_window_size
        # Add new data at the current position and its mirrored position
        self.buffer[current_position] = new_data
        self.buffer[current_position + self.max_window_size] = new_data
        # Update the count of items added
        self.items_added += 1

    def get_current_window(self):
        # Determine the current window size (it grows until it reaches max_window_size)
        current_window_size = min(self.items_added, self.max_window_size)
        start_pos = self.items_added % self.max_window_size
        if self.items_added <= self.max_window_size:
            return self.buffer[:current_window_size]
        else:
            return self.buffer[start_pos:start_pos + self.max_window_size]

# Example usage
if __name__ == "__main__":
    max_window_size = 5
    # Example: Specify the data type as integer
    streaming_window = StreamingWindow(max_window_size, dtype=np.int_)
    streaming_window = StreamingWindow(max_window_size, dtype=np.float_)

    # Simulate adding data and printing the current window
    for i in np.arange(1, 11, 0.5):
        streaming_window.add_data(i)
        print(f"Current window after adding {i}: {streaming_window.get_current_window()}")
