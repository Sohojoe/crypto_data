from data_manifest import DataManifest
import matplotlib
from matplotlib import dates as mdates
import pandas as pd
from streaming_stock_indicators import CandleStickIndicator, StreamingStockIndicators, MovingAverageIndicator, WilliamsFractalsIndicator
matplotlib.use('TkAgg')  # Replace 'TkAgg' with 'Qt5Agg', 'WXAgg', etc.
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import mplfinance as mpf
from datetime import datetime, timezone


data_manifest = DataManifest('data')

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

begin = data_manifest.start_time
begin = datetime(2023, 1, 1).replace(tzinfo=timezone.utc)
# data_generator = data_manifest.stream_data_and_window(begin, product, platform, time_period)
# data_iter = iter(data_generator)
window_size = 100
streaming_stock_indicators = StreamingStockIndicators(data_manifest, window_size=window_size)
data_generator = streaming_stock_indicators.stream_data_and_window(
    begin, 
    product, 
    platform, 
    time_period, 
    indicators=[
        MovingAverageIndicator(window_size=window_size, lookback_period=10),
        WilliamsFractalsIndicator(window_size=window_size)
        ])
data_iter = iter(data_generator)

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


def plot_indicators(indicators):
    candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
    moving_average_indicator = next((indicator for indicator in indicators if isinstance(indicator, MovingAverageIndicator)), None)
    williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
    # rows = {key: value for indicator in indicators for key, value in indicator.rows.items()}
    rows = candle_stick_indicator.rows
    cs_dataframe = pd.DataFrame(rows)
    cs_dataframe = cs_dataframe.set_index('time')
    cs_dataframe['volume'] = cs_dataframe['volume'].astype(int)
    cs_dataframe.index = pd.to_datetime(cs_dataframe.index, unit='s')

    ax1.clear()
    ax2.clear()
    addplot = [
    ]
    if moving_average_indicator:
        ma_dataframe = pd.DataFrame(moving_average_indicator.rows)
        # add the data index to ma_data
        ma_dataframe.index = cs_dataframe.index
        addplot.append(mpf.make_addplot(ma_dataframe['sma'], type='line', color='orange', ax=ax1))
        addplot.append(mpf.make_addplot(ma_dataframe['ema'], type='line', color='green', ax=ax1))


    mpf.plot(
        cs_dataframe, type='candle', 
        style=my_style_background, 
        volume=ax2, ax=ax1,
        addplot=addplot)

    if williams_fractals_indicator:
        indices = np.where(williams_fractals_indicator.rows['higher_fractal'] > 0)[0]
        for i in indices:
            ax1.annotate('▲', (i, cs_dataframe['high'].iloc[i]), color=down_candle_color, 
                        xytext=(0, 10),
                        textcoords='offset points',
                        #  zorder=5, 
                        fontsize=14, ha='center')

        indices = np.where(williams_fractals_indicator.rows['lower_fractal'] > 0)[0]
        for i in indices:
            ax1.annotate('▼', (i, cs_dataframe['low'].iloc[i]-200), color=up_candle_color, 
                        xytext=(0, -8),
                        textcoords='offset points',
                        #  zorder=5, 
                        fontsize=14, ha='center')

    ax1.yaxis.label.set_color(text_white)
    ax2.yaxis.label.set_color(text_white)
    fig.canvas.draw()    

def animate(i):
    # step, window = next(data_iter)
    indicators = next(data_iter)
    plot_indicators(indicators)
    

ani = FuncAnimation(fig, animate, interval=50, cache_frame_data=False)
# animate(0)
plt.show()

print("---done---")
