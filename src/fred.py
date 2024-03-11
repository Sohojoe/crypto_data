from data_manifest import DataManifest
import numpy as np
import pandas as pd
from streaming_stock_indicators import CandleStickIndicator, StreamingStockIndicators, MovingAverageIndicator, WilliamsFractalsIndicator
from datetime import datetime, timezone
from visualize_indicators import VisualizeIndicators

# for step, window in data_manifest.stream_data_and_window(data_manifest.start_time, product, platform, time_period):
#     # step will be an array of floats and ints
#     print(step)
#     print(window)
#     print('---')

def run_experiment(product, platform, time_period, begin, data_manifest, slippage):
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

    # visualize_indicators = VisualizeIndicators()
    # visualize_indicators.visualize_iterator(data_iter)
    # exit()

    higher_count = 0
    higher_value = None
    lower_count = 0
    lower_value = None
    indicators = None
    start_cash = 1
    cash = start_cash
    coins = 0
    entry = None
    outcomes = []
    first_open = None


    while True:
        try:
            indicators = next(data_iter)
            candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
            williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
        except StopIteration:
            break

        open = candle_stick_indicator.rows['open'][-1] # use open so we can see on charts
        close = candle_stick_indicator.rows['close'][-1]
        low = candle_stick_indicator.rows['open'][-1] # use open so we can see on charts
        first_open = first_open if first_open else open
        if (williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
            higher_count += 1
            higher_value = candle_stick_indicator.rows['high'][-3]
        if (williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
            lower_count += 1
            lower_value = candle_stick_indicator.rows['low'][-3]
        if higher_value and cash and open > higher_value:
            entry_price = (open + (open*slippage))
            coins = cash / entry_price
            # print(f"buy {coins} for ${cash} - open: {open}, above higher: {higher_value}")
            cash = 0
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
            exit_price = (lower_value - (lower_value*slippage))
            cash = coins * exit_price
            return_percent = ((exit_price/entry_price)-1.)*100.
            outcomes.append(return_percent)
            coins = 0
            # visualize_indicators = VisualizeIndicators()
            # visualize_indicators.visualize_frame(indicators)
            lower_value = None


    print("----------------------")
    print(f"product: {product}, platform: {platform}, time_period: {time_period}, slippage: {slippage}")

    if coins:
        cash = coins * close
    total_return = cash
    total_return_percent = (total_return/start_cash)-1.
    print(f"total return: {total_return_percent:.2f}%")
    buy_and_hold_return = (start_cash / first_open) * close
    buy_and_hold_return_percent = (close/first_open)-1.
    print(f"hodl return: {buy_and_hold_return_percent:.2f}%")
    print(f"strategy is {total_return_percent/buy_and_hold_return_percent:.2f} * better/worse than hodl")

    # # plot a histogram of the outcomes
    # import matplotlib.pyplot as plt
    # import numpy as np
    # plt.hist(outcomes, bins=20)
    # plt.show()

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


    # visualize_indicators = VisualizeIndicators()
    # visualize_indicators.visualize_frame(indicators)



    # visualize_indicators.visualize_iterator(data_iter)

    # indicators = next(data_iter)
    # visualize_indicators.visualize_frame(indicators)
    # visualize_indicators = VisualizeIndicators()
    # indicators = next(data_iter)
    # visualize_indicators.visualize_frame(indicators)

data_manifest = DataManifest('data')
product = data_manifest.products[0]
platform = data_manifest.platforms[0]
begin = data_manifest.start_time
# begin = datetime(2023, 1, 1).replace(tzinfo=timezone.utc)
# data_generator = data_manifest.stream_data_and_window(begin, product, platform, time_period)
# data_iter = iter(data_generator)

# time_periods = ['1D', '6H', '1H', '15T', '1T']
# time_periods = ['1D', '6H', '1H', '15T']
# for time_period in time_periods:
#     slippage = .005
#     run_experiment(product, platform, time_period, begin, data_manifest, slippage)

slipages = [.001, .0025, .005, .01, .015, .02, .025, .03, .035, .04, .045, .05]
time_period = '1D'
for slippage in slipages:
    run_experiment(product, platform, time_period, begin, data_manifest, slippage)

print("---done---")
