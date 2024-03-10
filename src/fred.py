from data_manifest import DataManifest
import pandas as pd
from streaming_stock_indicators import CandleStickIndicator, StreamingStockIndicators, MovingAverageIndicator, WilliamsFractalsIndicator
from datetime import datetime, timezone
from visualize_indicators import VisualizeIndicators

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


visualize_indicators = VisualizeIndicators()
# visualize_indicators.visualize_iterator(data_iter)
    
indicators = next(data_iter)
visualize_indicators.visualize_frame(indicators)
visualize_indicators = VisualizeIndicators()
indicators = next(data_iter)
visualize_indicators.visualize_frame(indicators)

print("---done---")
