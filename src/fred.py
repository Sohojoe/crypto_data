from data_manifest import DataManifest
from streaming_window import StreamingWindow

# Example usage
window_size = 3  # Define the window size
streaming_window = StreamingWindow(window_size)

for i in range(10):
    new_data = [i*.5] * 5
    streaming_window.add_data(new_data)

    current_window = streaming_window.get_current_window()
    print("Current window shape:", current_window.shape)
    print(current_window)

data_manifest = DataManifest('data')

product = data_manifest.products[0]
platform = data_manifest.platforms[0]
time_period = '1H'

for step in data_manifest.stream_data(data_manifest.start_time, product, platform, time_period):
    # step will be an array of floats and ints
    step_as_str = [str(v) for k, v in step.items()]
    print(','.join(step_as_str))

time_period = '1M'
for step in data_manifest.stream_data(data_manifest.start_time, product, platform, time_period):
    # step will be an array of floats and ints
    step_as_str = [str(v) for k, v in step.items()]
    print(','.join(step_as_str))



print("---done---")