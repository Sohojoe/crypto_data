from typing import Union
from dataclasses import dataclass, field
import numpy as np
from streaming_window import StreamingWindow
from abc import ABC, abstractmethod
from typing import List, Dict, Type
from data_manifest import DataManifest


class Indicator(ABC):
    @abstractmethod    
    def step(self, 
            rows: Dict[str, np.ndarray], 
            indicators: List['Indicator']):
        pass

    @property
    @abstractmethod
    def keys(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def cur_step(self) -> Dict[str, np.number]:
        pass

    @property
    @abstractmethod
    def rows(self) -> Dict[str, np.ndarray]:
        pass



class StreamingStockIndicators:
    def __init__(self, data_manifest:DataManifest, window_size:int):
        self.window_size:int = window_size
        self.data_manifest:DataManifest = data_manifest

    def stream_data_and_window(self,
                start_time, 
                product, 
                platform, 
                time_period, 
                end_time = None,
                indicators:List[Indicator] = None,
                fill_window=False):
        if indicators is None:
            indicators = []

        candle_stick_indicator = CandleStickIndicator(
            window_size=self.window_size,
            start_time=start_time,
            product=product,
            platform=platform,
            time_period=time_period,
            end_time=end_time
            )
        
        for stream_data in self.data_manifest.stream_data(start_time, product, platform, time_period, end_time):
            avaliable_indicators = []
            candle_stick_indicator.step(avaliable_indicators, stream_data)
            avaliable_indicators.append(candle_stick_indicator)
            for indicator in indicators:
                indicator.step(avaliable_indicators)
                avaliable_indicators.append(indicator)

            if fill_window and candle_stick_indicator.rows['close'].shape[0] < self.window_size:
                continue
            yield avaliable_indicators

class CandleStickIndicator(Indicator):
    def __init__(self, 
                window_size: int,
                start_time,
                product, 
                platform, 
                time_period, 
                end_time = None,
            ):
        self.window_size = window_size
        self.start_time = start_time
        self.product = product
        self.platform = platform
        self.time_period = time_period
        self.end_time = end_time
        self._keys = ['low', 'high', 'open', 'close', 'volume', 'time']
        self.window = StreamingWindow(window_size=self.window_size, num_features=len(self.keys))
        row = self.keys.index('time')
        for i in range(self.window_size):
            self.window.set_cell(row, i, 0.)

    def step(self, 
            indicators: List[Indicator],
            stream_data):
        cur_step = {}
        cur_step["low"] = np.float64(stream_data['Low'])
        cur_step["high"] = np.float64(stream_data['High'])
        cur_step["open"] = np.float64(stream_data['Open'])
        cur_step["close"] = np.float64(stream_data['Close'])
        cur_step["volume"] = np.float64(stream_data['Volume'])
        cur_step["time"] = np.float64(DataManifest.convert_str_to_datetime(stream_data['Time']).timestamp())
        
        assert list(cur_step.keys()) == self.keys
        data = [cur_step[key] for key in self.keys]
        self.window.add_data(data)

    @property
    def keys(self) -> List[str]:
        return self._keys

    @property
    def cur_step(self) -> Dict[str, np.number]:
        return {key: value[-1] for key, value in self.rows.items()}

    @property
    def rows(self) -> Dict[str, np.ndarray]:
        # return dict(zip(self.keys, self.window.get_current_window()))
        return {key: self.window.get_current_window()[i, :] for i, key in enumerate(self._keys)}        

class MovingAverageIndicator(Indicator):
    def __init__(self, window_size: int, lookback_period:int):
        self.window_size = window_size
        self._keys = ['sma', 'ema']
        self.window = StreamingWindow(window_size=self.window_size, num_features=len(self.keys))
        self.lookback_period = lookback_period

    def step(self, 
            indicators: List[Indicator]):
        
        candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
        rows = candle_stick_indicator.rows

        sma = np.nan
        ema= np.nan
        if len(rows['close']) >= self.lookback_period:
            view = rows['close'][-self.lookback_period:]  # Select the most recent 'window' data points
            sma = np.mean(view)  # Calculate the mean of these points
            recent_value = view[-1]  # Get the most recent data point
            last_ema = self.rows['ema'][-1] if not np.isnan(self.rows['ema'][-1]) else recent_value
            alpha = 2 / (self.lookback_period + 1)
            ema = (recent_value - last_ema) * alpha + last_ema         
        cur_step = {}
        cur_step['sma'] = sma
        cur_step['ema'] = ema

        data = [cur_step[key] for key in self.keys]
        self.window.add_data(data)

    @property
    def keys(self) -> List[str]:
        return self._keys

    @property
    def cur_step(self) -> Dict[str, np.number]:
        return {key: value[-1] for key, value in self.rows.items()}

    @property
    def rows(self) -> Dict[str, np.ndarray]:
        # return dict(zip(self.keys, self.window.get_current_window()))
        return {key: self.window.get_current_window()[i, :] for i, key in enumerate(self._keys)}
    

class WilliamsFractalsIndicator(Indicator):
    def __init__(self, window_size: int):
        self.window_size = window_size
        self._keys = ['lower_fractal', 'higher_fractal']
        self.window = StreamingWindow(window_size=self.window_size, num_features=len(self.keys))

    def step(self, 
            indicators: List[Indicator]):

        candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
        rows = candle_stick_indicator.rows

        # cur step is always 0 are we are looking forward
        cur_step = {}
        cur_step['lower_fractal'] = np.nan
        cur_step['higher_fractal'] = np.nan
        data = [cur_step[key] for key in self.keys]
        self.window.add_data(data)

        window_priods = 2 + 1 + 2
        if len(rows['close']) < window_priods:
            return

        low_idx = np.argmin(rows['low'][-5:])
        if int(low_idx) == 2:
            row = self.keys.index('lower_fractal')
            self.window.set_cell(row, -3, 1.)
        high_idx = np.argmax(rows['high'][-5:])
        if int(high_idx) == 2:
            row = self.keys.index('higher_fractal')
            self.window.set_cell(row, -3, 1.)

    @property
    def keys(self) -> List[str]:
        return self._keys

    @property
    def cur_step(self) -> Dict[str, np.number]:
        return {key: value[-1] for key, value in self.rows.items()}

    @property
    def rows(self) -> Dict[str, np.ndarray]:
        # return dict(zip(self.keys, self.window.get_current_window()))
        return {key: self.window.get_current_window()[i, :] for i, key in enumerate(self._keys)}