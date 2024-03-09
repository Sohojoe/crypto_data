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
            cur_step: Dict[str, np.number],
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
        self.keys:List[str] = ['low', 'high', 'open', 'close', 'volume', 'time']

    def stream_data_and_window(self,
                start_time, 
                product, 
                platform, 
                time_period, 
                indicators:List[Indicator] = None,
                fill_window=True):
        if indicators is None:
            indicators = []
        window = StreamingWindow(window_size=self.window_size, num_features=len(self.keys))
        
        for step in self.data_manifest.stream_data(start_time, product, platform, time_period):
            cur_step = {}
            cur_step["low"] = np.float64(step['Low'])
            cur_step["high"] = np.float64(step['High'])
            cur_step["open"] = np.float64(step['Open'])
            cur_step["close"] = np.float64(step['Close'])
            cur_step["volume"] = np.float64(step['Volume'])
            cur_step["time"] = np.float64(self.data_manifest.convert_str_to_datetime(step['Time']).timestamp())
            
            # assert the stock_state keys are the same and same order as self.keys
            assert list(cur_step.keys()) == self.keys
            data = [cur_step[key] for key in self.keys]
            window.add_data(data)
            current_window = window.get_current_window()
            rows = {}
            rows["low"] = current_window[0, :]
            rows["high"] = current_window[1, :]
            rows["open"] = current_window[2, :]
            rows["close"] = current_window[3, :]
            rows["volume"] = current_window[4, :]
            rows["time"] = current_window[5, :]

            avaliable_indicators = []
            for indicator in indicators:
                indicator.step(rows, cur_step, avaliable_indicators)
                avaliable_indicators.append(indicator)

            for indicator in indicators:
                cur_step = indicator.cur_step
                rows = indicator.rows

            if fill_window and current_window.shape[1] == self.window_size:
                yield cur_step, rows


class MovingAverageIndicator(Indicator):
    def __init__(self, window_size: int, lookback_period:int):
        self.window_size = window_size
        self._keys = ['sma', 'ema']
        self.window = StreamingWindow(window_size=self.window_size, num_features=len(self.keys))
        self.lookback_period = lookback_period

    def step(self, 
            rows: Dict[str, np.ndarray], 
            cur_step: Dict[str, np.number],
            indicators: List[Indicator]):
        
        sma = np.nan
        ema= np.nan
        if len(rows['close']) >= self.lookback_period:
            view = rows['close'][-self.lookback_period:]  # Select the most recent 'window' data points
            sma = np.mean(view)  # Calculate the mean of these points
            recent_value = view[-1]  # Get the most recent data point
            last_ema = self.rows['ema'][-1] if len(self.rows['ema']) > 0 else sma
            alpha = 2 / (self.lookback_period + 1)
            ema = (recent_value - last_ema) * alpha + last_ema         
        cur_step['sma'] = sma
        cur_step['ema'] = ema

        data = [cur_step[key] for key in self.keys]
        self.window.add_data(data)

        for k in self._keys:
            rows[k] = self.rows[k]

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