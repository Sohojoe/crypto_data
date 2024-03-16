import matplotlib
from trade import Trade
matplotlib.use('TkAgg')  # Replace 'TkAgg' with 'Qt5Agg', 'WXAgg', etc.
from matplotlib import dates as mdates
import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from streaming_stock_indicators import CandleStickIndicator, StreamingStockIndicators, MovingAverageIndicator, WilliamsFractalsIndicator
import pandas as pd
import numpy as np
from datetime import datetime, timezone

class VisualizeIndicators():
    def __init__(self):
        # Initialization with visualization settings (colors, etc.)
        self.background_color = '#161A25'
        self.up_candle_color = '#089981'
        self.down_candle_color = '#F23645'
        self.up_volume_color = '#305D5D'
        self.down_volume_color = '#783A3B'
        self.text_white = '#D4D6DD'
        self.line_color = '#2A2E38'
        self.soft_green_color = '#a5d6a7'
        self.soft_red_color = '#faa1a4'
        self.soft_yellow_color = '#fff59d'
        self.soft_orange_color = '#ffcc80'
        self.soft_blue_color = '#90bff9'
        self.soft_pink_color = '#f48fb1'
        self.soft_purple_color = '#ce93d8'
        
        #self.soft_ = '#xxxxxx'
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

    def visualize_frame(self, indicators):
        self._render_indicators(indicators)
        self.fig.canvas.draw()
        plt.show()

    def _render_indicators(self, indicators):
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
        # cs_dataframe['volume'] = cs_dataframe['volume'].astype(int)
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
                self.ax1.annotate('▼', (i, cs_dataframe['low'].iloc[i]), color=self.up_candle_color, 
                            xytext=(0, -15),
                            textcoords='offset points',
                            #  zorder=5, 
                            fontsize=14, ha='center')

        self.ax1.yaxis.label.set_color(self.text_white)
        self.ax2.yaxis.label.set_color(self.text_white)
        #self.fig.canvas.draw()    

    def visualize_iterator(self, data_iter):
        """
        Render enumerated data, continuing until the enumerator is empty.
        
        Parameters:
        - data_iter: An iterator over the data sets to be visualized.
        """
        # Implementation to visualize each set of data until the enumerator is empty.
        def animate(indicators):
            # try:
            #     indicators = next(data_iter)
            # except StopIteration:
            #     break            
            # indicators = next(data_iter)
            self._render_indicators(indicators)
            self.fig.canvas.draw()    


        ani = FuncAnimation(self.fig, animate, frames=data_iter, interval=50, cache_frame_data=False)
        # animate(0)
        plt.show()

    def visualize_trade(self, trade:Trade):
        self._render_indicators(trade.close_indicators)
        candle_stick_indicator = next((indicator for indicator in trade.close_indicators if isinstance(indicator, CandleStickIndicator)), None)
        # open
        open_time = trade.open_time
        open_price = trade.entry_price
        print(trade)
        try:
            open_idx = np.where(candle_stick_indicator.rows["time"] == open_time)[0][0]
            # self.ax1.hlines(y=open_price, xmin=xmax_value, xmax=open_idx, colors=self.text_white, linestyles='dashed')
            # self.ax1.hlines(y=open_price, xmin=open_idx, xmax=self.ax1.get_xlim()[1], colors=self.text_white, linestyles='dashed')
            idx_fraction = open_idx / len(candle_stick_indicator.rows["time"]) 
            self.ax1.axhline(
                y=open_price, 
                xmin=0,#idx_fraction, 
                xmax=1, 
                color=self.soft_yellow_color, alpha=0.5, linestyle='dashed')
            # self.ax1.hlines(y=open_price, xmin=open_idx_fraction, xmax=1, color=self.text_white, linestyle='dashed')
            self.ax1.annotate(f'Open\n{open_price}', (open_idx, open_price), color=self.soft_yellow_color, 
                xytext=(0, -50),
                textcoords='offset points',
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color=self.soft_yellow_color),  # Arrow styling
                fontsize=14, ha='center', va='top')
            # close
        except IndexError:
            pass
        close_time = trade.close_time
        close_price = trade.exit_price
        close_idx = np.where(candle_stick_indicator.rows["time"] == close_time)[0][0]
        close_color = self.soft_green_color if trade.return_percent > 0 else self.soft_red_color
        self.ax1.axhline(
            y=close_price, 
            xmin=0,#idx_fraction, 
            xmax=1, 
            color=close_color, alpha=0.5, linestyle='dashed')
        self.ax1.annotate(f'Close\n{close_price}', (close_idx, close_price), color=close_color, 
            xytext=(0, 50),
            textcoords='offset points',
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color=close_color),  # Arrow styling
            fontsize=14, ha='center', va='top')
        # show p&l in top left so should be in screen position
        p_and_l = trade.return_percent * 100
        self.ax1.annotate(f'p&l:{p_and_l:.2f}%', (.0, .95), color=self.text_white, 
                    xycoords='axes fraction',
                    # xycoords='figure fraction',
                    # xycoords='subfigure fraction',
                    xytext=(00, 0),
                    textcoords='offset points',
                    #  zorder=5, 
                    fontsize=14, ha='left', va='center')
        self.fig.canvas.draw()    

        plt.show()
