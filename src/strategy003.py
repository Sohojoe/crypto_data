from ast import List
from data_manifest import DataManifest
import numpy as np
import pandas as pd
from streaming_stock_indicators import CandleStickIndicator, StreamingStockIndicators, MovingAverageIndicator, WilliamsFractalsIndicator
from datetime import datetime, timezone
from trade import Trade
from visualize_indicators import VisualizeIndicators

# for step, window in data_manifest.stream_data_and_window(data_manifest.start_time, product, platform, time_period):
#     # step will be an array of floats and ints
#     print(step)
#     print(window)
#     print('---')

def run_experiment(product, platform, time_period, begin, data_manifest, slippage, end_time=None):
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
            ],
        end_time=end_time)
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
    first_open = None

    open_trades: List[Trade] = []
    closed_trades: List[Trade] = []

    df = Trade.create_emptpy_dataframe()

    while True:
        try:
            indicators = next(data_iter)
            candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
            williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
        except StopIteration:
            break

        open = candle_stick_indicator.rows['open'][-1] # use open so we can see on charts
        close = candle_stick_indicator.rows['close'][-1]
        high = candle_stick_indicator.rows['high'][-1] 
        low = candle_stick_indicator.rows['open'][-1] 
        first_open = first_open if first_open else open
        if (williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
            higher_count += 1
            higher_value = candle_stick_indicator.rows['high'][-3]
        if (williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
            lower_count += 1
            lower_value = candle_stick_indicator.rows['low'][-3]
        if higher_value and cash and high > higher_value:
            trade = Trade.open_trade(product, platform, time_period, candle_stick_indicator.cur_step['time'], slippage, higher_value, cash)
            cash = 0
            coins += trade.coins
            higher_value = None
            open_trades.append(trade)
            # debug = Trade.create_emptpy_dataframe()
            # pd.options.display.float_format = '{:,.3f}'.format
            # trade.add_row_to_dataframe(debug)
            # print(debug)
            # visualize_indicators = VisualizeIndicators()
            # visualize_indicators.visualize_frame(indicators)
        if lower_value and coins and low < lower_value:
            for trade in open_trades.copy():
                cash += trade.close(candle_stick_indicator.cur_step['time'], lower_value)
                coins -= trade.coins
                open_trades.remove(trade)
                closed_trades.append(trade)

            lower_value = None


    print("----------------------")
    print(f"product: {product}, platform: {platform}, time_period: {time_period}, slippage: {slippage}")

    for trade in open_trades.copy():
        cash += trade.close(candle_stick_indicator.cur_step['time'], lower_value)
        open_trades.remove(trade)
        closed_trades.append(trade)

    for trade in closed_trades:
        trade.add_row_to_dataframe(df)
    # print dataframe as csv
    # print(df.to_csv())
    
    if len(closed_trades) == 0:
        return None

    total_return = cash
    total_return_percent = (total_return/start_cash)-1.
    # print(f"total return: {total_return_percent:.2f}%")
    buy_and_hold_return = (start_cash / first_open) * close
    buy_and_hold_return_percent = (close/first_open)-1.
    # print(f"hodl return: {buy_and_hold_return_percent:.2f}%")
    # print(f"strategy is {total_return_percent/buy_and_hold_return_percent:.2f} * better/worse than hodl")

    # # # plot a histogram of the outcomes
    # # import matplotlib.pyplot as plt
    # # import numpy as np
    # # plt.hist(outcomes, bins=20)
    # # plt.show()

    # print(f"number of trades: {len(closed_trades)}")
    # # print number of winning / loosing trades
    return_percentages = [x.return_percent for x in closed_trades]
    # print(f"number of winning trades: {len([x.return_percent for x in closed_trades if x.return_percent > 0])}")
    # print(f"number of loosing trades: {len([x.return_percent for x in closed_trades if x.return_percent < 0])}")
    average_return = np.mean(return_percentages)
    # print(f"average_return: {average_return:.2f}")

    prob_profit = (len([x for x in return_percentages if x > 0]) / len(return_percentages))*100.
    prob_loss = (len([x for x in return_percentages if x < 0]) / len(return_percentages))*100.
    # print(f"prob_profit: {prob_profit:.2f}%, prob_loss: {prob_loss:.2f}%")

    # # calculate average win/loss ratio
    avg_win = np.mean([x for x in return_percentages if x > 0])
    avg_loss = np.mean([x for x in return_percentages if x < 0])
    # print(f"avg_win: {avg_win:.2f}, avg_loss: {avg_loss:.2f}")

    results = {
        "roi": total_return_percent,
        "hold_roi": buy_and_hold_return_percent,
        "vs_hodl": total_return_percent/buy_and_hold_return_percent,
        "trades": len(closed_trades),
        "winning": len([x.return_percent for x in closed_trades if x.return_percent > 0]),
        "loosing": len([x.return_percent for x in closed_trades if x.return_percent < 0]),
        "ave_return": average_return,
        "prob_profit": prob_profit,
        "prob_loss": prob_loss,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "time_period": time_period,
        "slippage": slippage,
        "product": product,
        "platform": platform,
        }
    
    return results


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

if False:
    # time_periods = ['1D', '6H', '1H', '15T', '1T']
    time_periods = ['1D', '6H', '1H', '15T']
    all_results = []
    slippages = [0, 0.005, 0.01]
    for time_period in time_periods:
        for slippage in slippages:
            result = run_experiment(product, platform, time_period, begin, data_manifest, slippage)
            all_results.append(result)
    # all_results is a list of dicts, please turn it into a dataframe
    df = pd.DataFrame(all_results)
    pd.options.display.float_format = '{:,.3f}'.format
    print(df)
    print(df.to_csv())
if True:
    print("--- compare start/end dates ---")
    dates = [
        # bitcoin halfending epocs
        # Jan 3 2009
        # November 28, 2012
        # July 9, 2016
        # May 11, 2020
        # April 20 2024
        # (datetime(2009, 1, 3), datetime(2012, 11, 28)),
        # (datetime(2012, 11, 28), datetime(2016, 7, 9)),
        (datetime(2016, 7, 9), datetime(2020, 5, 11)),
        (datetime(2020, 5, 11), datetime(2024, 4, 20)),
        (datetime(2024, 4, 20), datetime(2028, 1, 1)),
        # years
        (datetime(2016, 1, 1), datetime(2017, 12, 31)),
        (datetime(2017, 1, 1), datetime(2018, 12, 31)),
        (datetime(2018, 1, 1), datetime(2019, 12, 31)),
        (datetime(2019, 1, 1), datetime(2020, 12, 31)),
        (datetime(2020, 1, 1), datetime(2021, 12, 31)),
        (datetime(2021, 1, 1), datetime(2022, 12, 31)),
        (datetime(2022, 1, 1), datetime(2023, 12, 31)),
        (datetime(2023, 1, 1), datetime(2024, 12, 31)),
        (datetime(2024, 1, 1), datetime(2025, 12, 31)),
    ]
    all_results = []

    for start, end in dates:
        start = start.replace(tzinfo=timezone.utc)
        end = end.replace(tzinfo=timezone.utc)
        result = run_experiment(product, platform, '1D', start, data_manifest, 0.005, )
        if result is None:
            continue
        result['start'] = start
        result['end'] = end
        all_results.append(result)
    df = pd.DataFrame(all_results)
    pd.options.display.float_format = '{:,.3f}'.format
    print(df)
    print(df.to_csv())


# slipages = [.001, .0025, .005, .01, .015, .02, .025, .03, .035, .04, .045, .05]
# time_period = '1D'
# for slippage in slipages:
#     run_experiment(product, platform, time_period, begin, data_manifest, slippage)

print("---done---")
