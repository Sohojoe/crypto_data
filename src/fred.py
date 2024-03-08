from data_manifest import DataManifest
import matplotlib
from matplotlib import dates as mdates
import pandas as pd
matplotlib.use('TkAgg')  # Replace 'TkAgg' with 'Qt5Agg', 'WXAgg', etc.
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import mplfinance as mpf


data_manifest = DataManifest('data', window_size=100)

product = data_manifest.products[0]
platform = data_manifest.platforms[0]
# time_period = '1H'
time_period = '1D'
# time_period = '1M'

# for step, window in data_manifest.stream_data_and_window(data_manifest.start_time, product, platform, time_period):
#     # step will be an array of floats and ints
#     print(step)
#     print(window)
#     print('---')

data_generator = data_manifest.stream_data_and_window(data_manifest.start_time, product, platform, time_period)
data_iter = iter(data_generator)


# def show_plot(window_data):
#     data = pd.DataFrame(window_data.T[:, :-1], index=window_data[-1], columns=['Low', 'High', 'Open', 'Close', 'Volume'])
#     data['Volume'] = data['Volume'].astype(int)
#     data.index = pd.to_datetime(data.index, unit='s')
#     mpf.plot(data, type='candle', style='charles', volume=True)

# for _ in range(10):
#     step, window = next(data_iter)
#     show_plot(window)

background_color = '#161A25'
up_candle_color = '#089981'
down_candle_color = '#F23645'
up_volume_color = '#305D5D'
down_volume_color = '#783A3B'
text_white = '#D4D6DD'
line_color = '#2A2E38'
# background_color = '#808080'


my_style = {'candle'  : {'up':up_candle_color, 'down':down_candle_color},
            'edge'    : {'up':up_candle_color, 'down':down_candle_color},
            'wick'    : {'up':up_candle_color, 'down':down_candle_color},
            'ohlc'    : {'up':up_candle_color, 'down':down_candle_color},
            'volume'  : {'up':up_volume_color, 'down':down_volume_color},
            'vcedge'  : {'up':up_volume_color, 'down':down_volume_color},
            'vcdopcod': False, # Volume Color is Per Price Change On Day
            'alpha'   : 1.,# 0.9,
            }

my_style_background = mpf.make_mpf_style(
    marketcolors=my_style, 
    facecolor=background_color,  # Background color
    edgecolor='inherit',  # Use market colors for edges
    figcolor=background_color,  # Figure background color
    gridcolor=line_color,
    gridstyle='-.',  # Custom grid style
    y_on_right=True,  # Y-axis labels on the right
    rc={'font.color': text_white}  # Text color
)

fig = plt.figure(figsize=(8, 6), facecolor=background_color)
ax1 = fig.add_axes([0.1, 0.3, 0.8, 0.6])
ax1.set_facecolor(background_color)
ax1.tick_params(colors=text_white, labelcolor=text_white)
ax1.yaxis.label.set_color(text_white)
ax1.xaxis.label.set_color(text_white)
ax1.set_ylabel('Price', color=text_white)
for spine in ax1.spines.values():
    spine.set_color(line_color)

ax2 = fig.add_axes([0.1, 0.1, 0.8, 0.2], sharex=ax1)
ax2.set_facecolor(background_color)
ax2.tick_params(colors=text_white, labelcolor=text_white)
ax2.yaxis.label.set_color(text_white)
ax2.xaxis.label.set_color(text_white)
ax2.set_ylabel('Volume', color=text_white)
for spine in ax2.spines.values():
    spine.set_color(line_color)

def find_fractals(data):
    # Assuming 'data' is a DataFrame with 'High' and 'Low' columns
    upward_fractals = []
    downward_fractals = []
    
    for i in range(2, len(data) - 2):
        # Use .iloc for positional indexing
        if data['High'].iloc[i] > data['High'].iloc[i-1] and data['High'].iloc[i] > data['High'].iloc[i-2] and data['High'].iloc[i] > data['High'].iloc[i+1] and data['High'].iloc[i] > data['High'].iloc[i+2]:
            # upward_fractals.append(data.index[i])
            upward_fractals.append(i)
        if data['Low'].iloc[i] < data['Low'].iloc[i-1] and data['Low'].iloc[i] < data['Low'].iloc[i-2] and data['Low'].iloc[i] < data['Low'].iloc[i+1] and data['Low'].iloc[i] < data['Low'].iloc[i+2]:
            # downward_fractals.append(data.index[i])
            upward_fractals.append(i)
    return upward_fractals, downward_fractals

def animate(i):
    step, window = next(data_iter)
    data = pd.DataFrame(window.T[:, :-1], index=window[-1], columns=['Low', 'High', 'Open', 'Close', 'Volume'])
    data['Volume'] = data['Volume'].astype(int)
    data.index = pd.to_datetime(data.index, unit='s')

    ax1.clear()
    ax2.clear()
    mpf.plot(
        data, type='candle', 
        style=my_style_background, 
        volume=ax2, ax=ax1)

    upward_fractals, downward_fractals = find_fractals(data)
    for i in upward_fractals:
        ax1.annotate('▲', (i, data['High'].iloc[i]), color=down_candle_color, 
                     xytext=(0, 10),
                     textcoords='offset points',
                    #  zorder=5, 
                     fontsize=14, ha='center')
    for i in upward_fractals:
        ax1.annotate('▼', (i, data['Low'].iloc[i]-10), color=up_candle_color, 
                     xytext=(0, -8),
                     textcoords='offset points',
                    #  zorder=5, 
                     fontsize=14, ha='center')

    ax1.yaxis.label.set_color(text_white)
    ax2.yaxis.label.set_color(text_white)
    fig.canvas.draw()
    

ani = FuncAnimation(fig, animate, interval=500, cache_frame_data=False)
# animate(0)
plt.show()

print("---done---")
