from ast import List
from data_manifest import DataManifest
import numpy as np
import pandas as pd
from streaming_stock_indicators import CandleStickIndicator, StreamingStockIndicators, MovingAverageIndicator, WilliamsFractalsIndicator
from datetime import datetime, timezone
from trade import Trade
from visualize_indicators import VisualizeIndicators


data_manifest = DataManifest('data')
product = data_manifest.products[0]
platform = data_manifest.platforms[0]
begin = data_manifest.start_time
# begin = datetime(2023, 1, 1).replace(tzinfo=timezone.utc)
# data_generator = data_manifest.stream_data_and_window(begin, product, platform, time_period)
# data_iter = iter(data_generator)

# time_periods = ['1D', '6H', '1H', '15T', '1T']
# time_periods = ['1D', '6H', '1H', '15T']
time_periods = ['1D']
all_results = []
slippages = [0, 0.005, 0.01]
for time_period in time_periods:
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

    visualize_indicators = VisualizeIndicators()
    visualize_indicators.visualize_iterator(data_iter)


print("---done---")
