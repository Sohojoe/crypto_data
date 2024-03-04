import unittest
import numpy as np
from streaming_window import StreamingWindow  # Ensure this points to the correct module where StreamingWindow is defined

class TestStreamingWindow(unittest.TestCase):
    def setUp(self):
        self.window_size = 512
        self.num_features = 5
        self.streaming_window = StreamingWindow(self.window_size, self.num_features)
    
    def test_add_data_increases_data_count(self):
        initial_count = self.streaming_window.data_count
        self.streaming_window.add_data(np.random.rand(self.num_features))
        self.assertEqual(self.streaming_window.data_count, initial_count + 1, "Data count should increase by 1 after adding data.")
        
    def test_get_current_window_shape(self):
        for _ in range(10):
            self.streaming_window.add_data(np.random.rand(self.num_features))
        expected_shape = (self.num_features, 10)
        self.assertEqual(self.streaming_window.get_current_window().shape, expected_shape, "Current window shape should match the number of features and timesteps of data added.")
        
    def test_window_wraps_correctly(self):
        # Fill the window to its capacity
        for _ in range(self.window_size * 2):  # Fill beyond the window size to test wrapping
            self.streaming_window.add_data(np.random.rand(self.num_features))
        self.assertEqual(self.streaming_window.get_current_window().shape, (self.num_features, self.window_size), "Window should wrap correctly and only contain the most recent window_size columns of data.")
        
    def test_data_values(self):
        test_data = np.array([np.arange(self.num_features) for _ in range(10)])
        for data in test_data:
            self.streaming_window.add_data(data)
        retrieved_data = self.streaming_window.get_current_window()
        np.testing.assert_array_equal(retrieved_data[:, -test_data.shape[0]:], test_data.T, "The most recent data added should match the data retrieved from the window.")

if __name__ == '__main__':
    unittest.main()
