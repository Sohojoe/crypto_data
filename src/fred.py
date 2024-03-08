from data_manifest import DataManifest
import matplotlib
import pandas as pd
matplotlib.use('TkAgg')  # Replace 'TkAgg' with 'Qt5Agg', 'WXAgg', etc.
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import mplfinance as mpf


data_manifest = DataManifest('data', window_size=50)

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


def show_plot(window_data):
    data = pd.DataFrame(window_data.T[:, :-1], index=window_data[-1], columns=['Low', 'High', 'Open', 'Close', 'Volume'])
    data['Volume'] = data['Volume'].astype(int)
    data.index = pd.to_datetime(data.index, unit='s')
    mpf.plot(data, type='candle', style='charles', volume=True)

for _ in range(10):
    step, window = next(data_iter)
    show_plot(window)

print("---done---")
