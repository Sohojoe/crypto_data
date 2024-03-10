from data_manifest import DataManifest
import numpy as np
import pandas as pd
from streaming_stock_indicators import CandleStickIndicator, StreamingStockIndicators, MovingAverageIndicator, WilliamsFractalsIndicator
from datetime import datetime, timezone
from visualize_indicators import VisualizeIndicators

data_manifest = DataManifest('data')

product = data_manifest.products[0]
platform = data_manifest.platforms[0]
time_period = '1D'
# time_period = '6H'
# time_period = '1H'
# time_period = '15T'
# time_period = '1T'


# for step, window in data_manifest.stream_data_and_window(data_manifest.start_time, product, platform, time_period):
#     # step will be an array of floats and ints
#     print(step)
#     print(window)
#     print('---')

begin = data_manifest.start_time
# begin = datetime(2023, 1, 1).replace(tzinfo=timezone.utc)
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
        # MovingAverageIndicator(window_size=window_size, lookback_period=10),
        WilliamsFractalsIndicator(window_size=window_size)
        ])
data_iter = iter(data_generator)

visualize_indicators = VisualizeIndicators()
higher_count = 0
higher_value = None
lower_count = 0
lower_value = None
indicators = None
cash = 1000
coins = 0
entry = None
outcomes = []



while True:
    try:
        indicators = next(data_iter)
        candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
        williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
    except StopIteration:
        break

    # close = candle_stick_indicator.rows['close'][-1]
    open = candle_stick_indicator.rows['open'][-1] # use open so we can see on charts
    low = candle_stick_indicator.rows['open'][-1] # use open so we can see on charts
    if (williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
        higher_count += 1
        higher_value = candle_stick_indicator.rows['high'][-3]
    if (williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
        lower_count += 1
        lower_value = candle_stick_indicator.rows['low'][-3]
    if higher_value and cash and open > higher_value:
        coins = cash / open
        # print(f"buy {coins} for ${cash} - open: {open}, above higher: {higher_value}")
        cash = 0
        entry = open
        # visualize_indicators = VisualizeIndicators()
        # visualize_indicators.visualize_frame(indicators)
        higher_value = None
    # if lower_value and coins and open < lower_value:
    #     cash = coins * open
    #     return_percent = ((open/entry)-1.)*100.
    #     s = f"{return_percent:.2f}% bought at {entry}, sold at {open}, p&l: ${open - entry}"
    #     print(f"stop - return: {return_percent:.2f}% bought at {entry}, sold at {open}, p&l: ${open - entry}")
    #     outcomes.append(return_percent)
    #     coins = 0
    #     # visualize_indicators = VisualizeIndicators()
    #     # visualize_indicators.visualize_frame(indicators)
    #     lower_value = None
    if lower_value and coins and low < lower_value:
        cash = coins * lower_value
        return_percent = ((lower_value/entry)-1.)*100.
        s = f"{return_percent:.2f}% bought at {entry}, sold at {lower_value}, p&l: ${open - entry}"
        # print(f"stop - return: {return_percent:.2f}% bought at {entry}, sold at {lower_value}, p&l: ${lower_value - entry}")
        outcomes.append(return_percent)
        coins = 0
        # visualize_indicators = VisualizeIndicators()
        # visualize_indicators.visualize_frame(indicators)
        lower_value = None


# # plot a histogram of the outcomes
# import matplotlib.pyplot as plt
# import numpy as np
# plt.hist(outcomes, bins=20)
# plt.show()

print(f"product: {product}, platform: {platform}, time_period: {time_period}")
print(f"number of trades: {len(outcomes)}")
# print number of winning / loosing trades
print(f"number of winning trades: {len([x for x in outcomes if x > 0])}")
print(f"number of loosing trades: {len([x for x in outcomes if x < 0])}")
average_return = np.mean(outcomes)
print(f"average_return: {average_return:.2f}")

prob_profit = (len([x for x in outcomes if x > 0]) / len(outcomes))*100.
prob_loss = (len([x for x in outcomes if x < 0]) / len(outcomes))*100.
print(f"prob_profit: {prob_profit:.2f}%, prob_loss: {prob_loss:.2f}%")

# calculate average win/loss ratio
avg_win = np.mean([x for x in outcomes if x > 0])
avg_loss = np.mean([x for x in outcomes if x < 0])
print(f"avg_win: {avg_win:.2f}, avg_loss: {avg_loss:.2f}")



# calculate the probability of different outcomes
# so +/= <1%
# so +/= >=1%
# so +/= >=%
# so +/= >=5%
# so +/= >=10%
# so +/= >=15%
# so +/= >=20%
# so +/= >=25%



visualize_indicators = VisualizeIndicators()
visualize_indicators.visualize_frame(indicators)



visualize_indicators.visualize_iterator(data_iter)

# indicators = next(data_iter)
# visualize_indicators.visualize_frame(indicators)
# visualize_indicators = VisualizeIndicators()
# indicators = next(data_iter)
# visualize_indicators.visualize_frame(indicators)

print("---done---")
