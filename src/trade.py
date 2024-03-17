from dataclasses import dataclass, field, fields
from typing import List
import pandas as pd
import numpy as np
from streaming_stock_indicators import CandleStickIndicator, Indicator
import copy


@dataclass
class Trade:
    product: str
    platform: str
    time_period: str
    open_time: float
    slippage: float
    entry_price: float
    actual_entry_price: float
    coins: float
    open_indicators: List[Indicator]
    close_time: float = field(default=None)
    # time_open: float = field(default=None)
    return_percent: float = field(default=None)
    exit_price: float = field(default=None)
    actual_exit_price: float = field(default=None)
    close_indicators: List[Indicator] = field(default=None)

    def close(self, exit_price, close_indicators: List[Indicator]) -> float:
        candle_stick_indicator = next((indicator for indicator in close_indicators if isinstance(indicator, CandleStickIndicator)), None)
        actual_exit_price = exit_price - (exit_price * self.slippage)
        self.close_time = candle_stick_indicator.cur_step["time"]
        self.exit_price = exit_price
        self.actual_exit_price = actual_exit_price
        self.return_percent = (self.actual_exit_price / self.actual_entry_price) - 1.0
        cash = self.coins * self.exit_price
        self.close_indicators = copy.deepcopy(close_indicators)
        return cash

    @staticmethod
    def open_trade(
        slippage,
        entry_price,
        cash_to_spend,
        open_indicators: List[Indicator],
    ):
        actual_entry_price = entry_price + (entry_price * slippage)
        coins = cash_to_spend / actual_entry_price
        candle_stick_indicator = next((indicator for indicator in open_indicators if isinstance(indicator, CandleStickIndicator)), None)
        trade = Trade(
            product=candle_stick_indicator.product,
            platform=candle_stick_indicator.platform,
            time_period=candle_stick_indicator.time_period,
            open_time=candle_stick_indicator.cur_step["time"],
            # time_open=open_time,
            slippage=slippage,
            entry_price=entry_price,
            actual_entry_price=actual_entry_price,
            coins=coins,
            open_indicators=copy.deepcopy(open_indicators),
        )
        return trade

    @staticmethod
    def create_emptpy_dataframe():
        headers = [f.name for f in fields(Trade)]
        df = pd.DataFrame(columns=headers)
        # You don't need to explicitly set types here; it will be inferred upon assignment
        df.set_index("open_time", inplace=True)
        return df

    def add_row_to_dataframe(self, df):
        # Directly create a dict mapping field names to values
        row_dict = {f.name: getattr(self, f.name) for f in fields(Trade)}
        row_df = pd.DataFrame([row_dict], index=[self.open_time])
        df.loc[self.open_time] = row_dict
