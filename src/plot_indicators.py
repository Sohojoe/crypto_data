import matplotlib
matplotlib.use('TkAgg')  # Replace 'TkAgg' with 'Qt5Agg', 'WXAgg', etc.
from matplotlib import dates as mdates
import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from streaming_stock_indicators import CandleStickIndicator, StreamingStockIndicators, MovingAverageIndicator, WilliamsFractalsIndicator
import pandas as pd
import numpy as np


class PlotIndicators():
    def __init__(self):
        # Initialization with visualization settings (colors, etc.)
        self.background_color = '#161A25'
        self.up_candle_color = '#089981'
        self.down_candle_color = '#F23645'
        self.up_volume_color = '#305D5D'
        self.down_volume_color = '#783A3B'
        self.text_white = '#D4D6DD'
        self.line_color = '#2A2E38'
        # Additional settings can be added as needed
        my_style = {'candle'  : {'up':self.up_candle_color, 'down':self.down_candle_color},
            'edge'    : {'up':self.up_candle_color, 'down':self.down_candle_color},
            'wick'    : {'up':self.up_candle_color, 'down':self.down_candle_color},
            'ohlc'    : {'up':self.up_candle_color, 'down':self.down_candle_color},
            'volume'  : {'up':self.up_volume_color, 'down':self.down_volume_color},
            'vcedge'  : {'up':self.up_volume_color, 'down':self.down_volume_color},
            'vcdopcod': False, # Volume Color is Per Price Change On Day
            'alpha'   : 1.,# 0.9,
            }
        my_style_background = mpf.make_mpf_style(
            marketcolors=my_style, 
            facecolor=self.background_color,  # Background color
            edgecolor='inherit',  # Use market colors for edges
            figcolor=self.background_color,  # Figure background color
            gridcolor=self.line_color,
            gridstyle='-.',  # Custom grid style
            y_on_right=True,  # Y-axis labels on the right
            rc={'font.color': self.text_white}  # Text color
        )
        fig = plt.figure(figsize=(8, 6), facecolor=self.background_color)
        ax1 = fig.add_axes([0.1, 0.3, 0.8, 0.6])
        ax1.set_facecolor(self.background_color)
        ax1.tick_params(colors=self.text_white, labelcolor=self.text_white)
        ax1.yaxis.label.set_color(self.text_white)
        ax1.xaxis.label.set_color(self.text_white)
        ax1.set_ylabel('Price', color=self.text_white)
        for spine in ax1.spines.values():
            spine.set_color(self.line_color)

        ax2 = fig.add_axes([0.1, 0.1, 0.8, 0.2], sharex=ax1)
        ax2.set_facecolor(self.background_color)
        ax2.tick_params(colors=self.text_white, labelcolor=self.text_white)
        ax2.yaxis.label.set_color(self.text_white)
        ax2.xaxis.label.set_color(self.text_white)
        ax2.set_ylabel('Volume', color=self.text_white)
        for spine in ax2.spines.values():
            spine.set_color(self.line_color)

        self.ax1 = ax1
        self.ax2 = ax2
        self.my_style_background = my_style_background
        self.fig = fig

    def plot_indicators(self, indicators):
        self._plot_indicators(indicators)
        plt.show()

    def _plot_indicators(self, indicators):
        """
        Render a single set of indices for debugging and visualization.
        
        Parameters:
        - data: The data set to visualize. This should be structured in a way that it can be plotted directly.
        """
        # Implementation of the visualization logic for a single data set.
        candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
        moving_average_indicator = next((indicator for indicator in indicators if isinstance(indicator, MovingAverageIndicator)), None)
        williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
        # rows = {key: value for indicator in indicators for key, value in indicator.rows.items()}
        rows = candle_stick_indicator.rows
        cs_dataframe = pd.DataFrame(rows)
        cs_dataframe = cs_dataframe.set_index('time')
        cs_dataframe['volume'] = cs_dataframe['volume'].astype(int)
        cs_dataframe.index = pd.to_datetime(cs_dataframe.index, unit='s')

        self.ax1.clear()
        self.ax2.clear()
        addplot = [
        ]
        if moving_average_indicator:
            ma_dataframe = pd.DataFrame(moving_average_indicator.rows)
            # add the data index to ma_data
            ma_dataframe.index = cs_dataframe.index
            addplot.append(mpf.make_addplot(ma_dataframe['sma'], type='line', color='orange', ax=self.ax1))
            addplot.append(mpf.make_addplot(ma_dataframe['ema'], type='line', color='green', ax=self.ax1))


        mpf.plot(
            cs_dataframe, type='candle', 
            style=self.my_style_background, 
            volume=self.ax2, ax=self.ax1,
            addplot=addplot)

        if williams_fractals_indicator:
            indices = np.where(williams_fractals_indicator.rows['higher_fractal'] > 0)[0]
            for i in indices:
                self.ax1.annotate('▲', (i, cs_dataframe['high'].iloc[i]), color=self.down_candle_color, 
                            xytext=(0, 10),
                            textcoords='offset points',
                            #  zorder=5, 
                            fontsize=14, ha='center')

            indices = np.where(williams_fractals_indicator.rows['lower_fractal'] > 0)[0]
            for i in indices:
                self.ax1.annotate('▼', (i, cs_dataframe['low'].iloc[i]-200), color=self.up_candle_color, 
                            xytext=(0, -8),
                            textcoords='offset points',
                            #  zorder=5, 
                            fontsize=14, ha='center')

        self.ax1.yaxis.label.set_color(self.text_white)
        self.ax2.yaxis.label.set_color(self.text_white)
        self.fig.canvas.draw()    

    def plot_iterator(self, data_iter):
        """
        Render enumerated data, continuing until the enumerator is empty.
        
        Parameters:
        - data_iter: An iterator over the data sets to be visualized.
        """
        # Implementation to visualize each set of data until the enumerator is empty.
        def animate(i):
            # step, window = next(data_iter)
            indicators = next(data_iter)
            self._plot_indicators(indicators)

        ani = FuncAnimation(self.fig, animate, interval=50, cache_frame_data=False)
        # animate(0)
        plt.show()

