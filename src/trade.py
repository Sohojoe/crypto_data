from dataclasses import dataclass, field, fields
import pandas as pd
import numpy as np

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
    close_time: float = field(default=None)
    time_open: float = field(default=None)
    return_percent: float = field(default=None)
    exit_price: float = field(default=None)
    actual_exit_price: float = field(default=None)

    def close(self, close_time, exit_price):
        actual_exit_price = exit_price - (exit_price * self.slippage)
        self.close_time = close_time
        self.exit_price = exit_price
        self.actual_exit_price = actual_exit_price
        self.return_percent = ((self.actual_exit_price / self.actual_entry_price) - 1.)
        cash = self.coins * self.exit_price
        return cash

    @staticmethod
    def open_trade(product, platform, time_period, open_time, slippage, entry_price, cash_to_spend):
        actual_entry_price = entry_price + (entry_price * slippage)
        coins = cash_to_spend / actual_entry_price
        trade = Trade(
            product = product,
            platform = platform,
            time_period = time_period,
            open_time = open_time,
            time_open = open_time,
            slippage = slippage,
            entry_price = entry_price,
            actual_entry_price = actual_entry_price,
            coins = coins,
            )
        return trade
    

    @staticmethod
    def create_emptpy_dataframe():
        headers = [f.name for f in fields(Trade)]
        df = pd.DataFrame(columns=headers)
        # You don't need to explicitly set types here; it will be inferred upon assignment
        df.set_index('open_time', inplace=True)
        return df
    
    def add_row_to_dataframe(self, df):
        # Directly create a dict mapping field names to values
        row_dict = {f.name: getattr(self, f.name) for f in fields(Trade)}
        row_df = pd.DataFrame([row_dict], index=[self.open_time])
        df.loc[self.open_time] = row_dict