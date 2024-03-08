from data_manifest import DataManifest
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from streaming_window import StreamingWindow

data_manifest = DataManifest('data')

product = data_manifest.products[0]
platform = data_manifest.platforms[0]
time_period = '1H'
# time_period = '1M'

# for step, window in data_manifest.stream_data_and_window(data_manifest.start_time, product, platform, time_period):
#     # step will be an array of floats and ints
#     print(step)
#     print(window)
#     print('---')

data_generator = data_manifest.stream_data_and_window(data_manifest.start_time, product, platform, time_period)
data_iter = iter(data_generator)

# Create a figure and axis
fig, ax = plt.subplots()

# Initialize line objects for each data series
line_low, = ax.plot([], [], label='Low')
line_high, = ax.plot([], [], label='High')
line_open, = ax.plot([], [], label='Open')
line_close, = ax.plot([], [], label='Close')
line_volume, = ax.plot([], [], label='Volume')

# Set up the legend
ax.legend()

# Set up the axis labels and title
ax.set_xlabel('Time (or sequence index)')
ax.set_ylabel('Price/Volume')
ax.set_title('Simulated Stock Data')

def init():
    line_low.set_data([], [])
    line_high.set_data([], [])
    line_open.set_data([], [])
    line_close.set_data([], [])
    line_volume.set_data([], [])
    return line_low, line_high, line_open, line_close, line_volume

def update(frame):
    try:
        step, window = next(data_iter)
        x_values = np.arange(window.shape[1])

        line_low.set_data(x_values, window[0])
        line_high.set_data(x_values, window[1])
        line_open.set_data(x_values, window[2])
        line_close.set_data(x_values, window[3])
        line_volume.set_data(x_values, window[4])

        ax.set_xlim(0, x_values[-1])
        ax.set_ylim(np.min(window), np.max(window))

    except StopIteration:
        pass  # No more data

    return line_low, line_high, line_open, line_close, line_volume

ani = FuncAnimation(fig, update, frames=np.arange(100), init_func=init, blit=True)

plt.show()


# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation

# # Create a figure and axis
# fig, ax = plt.subplots()

# # Initialize line objects for each data series
# line_low, = ax.plot([], [], label='Low')
# line_high, = ax.plot([], [], label='High')
# line_open, = ax.plot([], [], label='Open')
# line_close, = ax.plot([], [], label='Close')
# line_volume, = ax.plot([], [], label='Volume')

# # Set up the legend
# ax.legend()

# # Set up the axis labels and title
# ax.set_xlabel('Time')
# ax.set_ylabel('Price/Volume')
# ax.set_title('Stock Data')

# def update(frame):
#     try:
#         # Retrieve the latest step and window data from your data source
#         step, window = next(data_iter)

#         # Update the data for each line
#         line_low.set_data(window[0])
#         line_high.set_data(window[1])
#         line_open.set_data(window[2])
#         line_close.set_data(window[3])
#         line_volume.set_data(window[4])

#         # Adjust the x-axis limits to show the latest data
#         ax.set_xlim(0, len(window[:, -1]))

#     except StopIteration:
#         # Handle the case when there is no more data
#         pass

#     # Return the updated lines
#     return line_low, line_high, line_open, line_close, line_volume

# ani = FuncAnimation(fig, update, interval=100, blit=True)

# # Display the plot
# plt.show()

# print("---done---")
