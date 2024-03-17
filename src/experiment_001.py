from datetime import datetime, timezone
from typing import Any, Dict, List
from data_manifest import DataManifest
from experiment import Experiment
import pandas as pd
from policy import Policy
from strategies import wf_buy_every_cross_strategy, wf_buy_every_open_strategy, wf_buy_on_cross_strategy, wf_buy_on_open_strategy, wf_sell_on_cross_strategy, wf_sell_on_open_strategy
from streaming_stock_indicators import CandleStickIndicator, Indicator, WilliamsFractalsIndicator
from trade import Trade


window_size = 100
data_manifest = DataManifest('data')
product = data_manifest.products[0]
platform = data_manifest.platforms[0]
# time_period="12H"
begin = data_manifest.start_time
slippage = 0.005
# begin = datetime(2023, 1, 1).replace(tzinfo=timezone.utc)

def create_indicators(window_size: int):
    indicators =[
            # MovingAverageIndicator(window_size=window_size, lookback_period=10),
            WilliamsFractalsIndicator(window_size=window_size)
            ]
    return indicators

buy_strategies = [
    wf_buy_on_open_strategy,
    wf_buy_on_cross_strategy,
    wf_buy_every_open_strategy,
    wf_buy_every_cross_strategy,
]

sell_strategies = [
    wf_sell_on_open_strategy,
    wf_sell_on_cross_strategy,
]

start_times_to_test = [
    # data_manifest.start_time,
    # datetime(2016, 1, 1).replace(tzinfo=timezone.utc),
    # datetime(2017, 1, 1).replace(tzinfo=timezone.utc),
    datetime(2018, 1, 1).replace(tzinfo=timezone.utc),
    # datetime(2019, 1, 1).replace(tzinfo=timezone.utc),
    # datetime(2020, 1, 1).replace(tzinfo=timezone.utc),
    # datetime(2021, 1, 1).replace(tzinfo=timezone.utc),
    # datetime(2022, 1, 1).replace(tzinfo=timezone.utc),
    # datetime(2023, 1, 1).replace(tzinfo=timezone.utc),
]

time_periods=[
    # "6H",
    # "12H",
    "1D",
    # "36H",
    "2D",
    "3D",
    "4D",
    # "5D",
    # "6D",
    # "7D",
]


experiments = [
    (buy, sell, begin, time_period) 
        for buy in buy_strategies 
        for sell in sell_strategies 
        for begin in start_times_to_test
        for time_period in time_periods
    ]

print(f"experiments: {len(experiments)}")

results = []

def should_plot(trade: Trade):
    return False
    # x = trade.return_percent > 0.3
    # return x

for buy_strategy, sell_strategie, begin, time_period in experiments:
    policy = Policy(
        buy_strategy=buy_strategy,
        sell_strategy=sell_strategie,
        slippage=slippage,
        start_cash=1
    )
    # 8 years
    end_time = begin.replace(year=begin.year+4)
    experment = Experiment(
        product=product,
        platform=platform,
        time_period=time_period,
        begin=begin,
        data_manifest=data_manifest,
        indicators=create_indicators(window_size),
        policy=policy,
        window_size=window_size,
        end_time=end_time)

    print(experment)
    result = experment.run()
    # print(experment)
    results.append(result)
    experment.plot(should_plot)

df = pd.DataFrame(results)
if "roi" in df.columns:
    df = df.sort_values('roi', ascending=False)
else:
    df = df.sort_values('expected_return', ascending=False)
pd.options.display.float_format = '{:,.3f}'.format
print(df.to_string())

print("--- end ---")