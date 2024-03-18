

from typing import List

from policy import Policy
from streaming_stock_indicators import Indicator
from trade import Trade



def buy_hodl_strategy(self: Policy):
    open = self.candle_stick_indicator.cur_step['open']
    if self.cash:
        self.open_trade(entry_price=open, cash_to_spend=self.cash)

def sell_hodl_strategy(self: Policy):
    return

def wf_buy_on_open_strategy(self: Policy):
    open = self.candle_stick_indicator.cur_step['open']
    close = self.candle_stick_indicator.cur_step['close']
    high = self.candle_stick_indicator.cur_step['high'] 
    low = self.candle_stick_indicator.cur_step['low']
    time = self.candle_stick_indicator.cur_step["time"]
    if not hasattr(self, 'higher_value'):
        self.higher_value = None
        self.lower_value = None
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    if (self.williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
        self.higher_value = self.candle_stick_indicator.rows['high'][-3]
    if (self.williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
        self.lower_value = self.candle_stick_indicator.rows['low'][-3]
    if self.higher_value and open > self.higher_value and self.cash:
        if self.open_trade(entry_price=open, cash_to_spend=self.cash):
            # note: buy signal is removed if we buy
            self.higher_value = None


def wf_sell_on_open_strategy(self: Policy):
    open = self.candle_stick_indicator.cur_step['open']
    close = self.candle_stick_indicator.cur_step['close']
    high = self.candle_stick_indicator.cur_step['high'] 
    low = self.candle_stick_indicator.cur_step['low']
    time = self.candle_stick_indicator.cur_step["time"]
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    if (self.lower_value and open < self.lower_value):
        num_closed = self.close_all_trades(exit_price=open)
        if num_closed:
            # note: we do not set lower_value to None as we want it as our stop loss
            # strategy_state["lower_value"] = None
            pass
        

def wf_buy_on_cross_strategy(self: Policy):
    open = self.candle_stick_indicator.cur_step['open']
    close = self.candle_stick_indicator.cur_step['close']
    high = self.candle_stick_indicator.cur_step['high'] 
    low = self.candle_stick_indicator.cur_step['low']
    time = self.candle_stick_indicator.cur_step["time"]
    if not hasattr(self, 'higher_value'):
        self.higher_value = None
        self.lower_value = None
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    if (self.williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
        self.higher_value = self.candle_stick_indicator.rows['high'][-3]
    if (self.williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
        self.lower_value = self.candle_stick_indicator.rows['low'][-3]
    if self.higher_value and high > self.higher_value and self.cash:
        if self.open_trade(entry_price=self.higher_value, cash_to_spend=self.cash):
            # note: buy signal is removed if we buy
            self.higher_value = None

def wf_sell_on_cross_strategy(self: Policy):
    open = self.candle_stick_indicator.cur_step['open']
    close = self.candle_stick_indicator.cur_step['close']
    high = self.candle_stick_indicator.cur_step['high'] 
    low = self.candle_stick_indicator.cur_step['low']
    time = self.candle_stick_indicator.cur_step["time"]
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    if (self.lower_value and low < self.lower_value):
        num_closed = self.close_all_trades(exit_price=self.lower_value)
        if num_closed:
            # note: we do not set lower_value to None as we want it as our stop loss
            # strategy_state["lower_value"] = None
            pass

def wf_buy_every_open_strategy(self: Policy):
    open = self.candle_stick_indicator.cur_step['open']
    close = self.candle_stick_indicator.cur_step['close']
    high = self.candle_stick_indicator.cur_step['high'] 
    low = self.candle_stick_indicator.cur_step['low']
    time = self.candle_stick_indicator.cur_step["time"]
    if not hasattr(self, 'higher_value'):
        self.higher_value = None
        self.lower_value = None
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    if (self.williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
        self.higher_value = self.candle_stick_indicator.rows['high'][-3]
    if (self.williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
        self.lower_value = self.candle_stick_indicator.rows['low'][-3]
    if self.higher_value and open > self.higher_value and self.cash:
        if self.open_trade(entry_price=open, cash_to_spend=self.cash):
            # note: do not remove the buy signal so we buy many times
            # strategy_state["higher_value"] = None
            pass

def wf_buy_every_cross_strategy(self: Policy):
    open = self.candle_stick_indicator.cur_step['open']
    close = self.candle_stick_indicator.cur_step['close']
    high = self.candle_stick_indicator.cur_step['high'] 
    low = self.candle_stick_indicator.cur_step['low']
    time = self.candle_stick_indicator.cur_step["time"]
    if not hasattr(self, 'higher_value'):
        self.higher_value = None
        self.lower_value = None
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    if (self.williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
        self.higher_value = self.candle_stick_indicator.rows['high'][-3]
    if (self.williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
        self.lower_value = self.candle_stick_indicator.rows['low'][-3]
    if self.higher_value and high > self.higher_value and self.cash:
        if self.open_trade(entry_price=self.higher_value, cash_to_spend=self.cash):
            # note: do not remove the buy signal so we buy many times
            # strategy_state["higher_value"] = None
            pass
#         strategy_state: Dict[str, Any], 
#         indicators: List[Indicator]
#         )->List[Trade]:
#     candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
#     williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
#     open = candle_stick_indicator.cur_step['open']
#     close = candle_stick_indicator.cur_step['close']
#     high = candle_stick_indicator.cur_step['high'] 
#     low = candle_stick_indicator.cur_step['low']
#     time = candle_stick_indicator.cur_step["time"]
#     cash = strategy_state.get("cash", 1)
#     # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
#     if (williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
#         strategy_state["higher_value"] = candle_stick_indicator.rows['high'][-3]
#     if (williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
#         strategy_state["lower_value"] = candle_stick_indicator.rows['low'][-3]
#     higher_value = strategy_state["higher_value"]
#     open_trades: List[Trade] = []    
#     if higher_value and high > higher_value and cash:
#         trade = Trade.open_trade(
#             slippage=slippage,
#             entry_price=higher_value,
#             cash_to_spend=cash,
#             open_indicators=indicators,
#         )
#         open_trades.append(trade)
#         # note: buy signal is removed if we buy
#         strategy_state["higher_value"] = None
#         if "cash" in strategy_state:
#             strategy_state["cash"] = 0
#     return open_trades

# def wf_sell_on_cross_strategy(
#         strategy_state: Dict[str, Any], 
#         indicators: List[Indicator], 
#         open_trades: List[Trade], 
#         force_close :bool = False
#         )->List[Trade]:
#     candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
#     williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
#     open = candle_stick_indicator.cur_step['open']
#     close = candle_stick_indicator.cur_step['close']
#     high = candle_stick_indicator.cur_step['high'] 
#     low = candle_stick_indicator.cur_step['low']
#     time = candle_stick_indicator.cur_step["time"]
#     # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
#     lower_value = strategy_state["lower_value"]
#     closed_trades = []
#     if (lower_value and low < lower_value) or force_close:
#         cash = strategy_state.get("cash", 1)
#         for trade in open_trades:
#             cash += trade.close(
#                 lower_value,
#                 indicators)
#             closed_trades.append(trade)
#         # note: we do not set lower_value to None as we want it as our stop loss
#         # strategy_state["lower_value"] = None
#         if "cash" in strategy_state:
#             strategy_state["cash"] = cash
#     return closed_trades

# def wf_buy_every_open_strategy(
#         strategy_state: Dict[str, Any], 
#         indicators: List[Indicator]
#         )->List[Trade]:
#     candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
#     williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
#     open = candle_stick_indicator.cur_step['open']
#     close = candle_stick_indicator.cur_step['close']
#     high = candle_stick_indicator.cur_step['high'] 
#     low = candle_stick_indicator.cur_step['low']
#     time = candle_stick_indicator.cur_step["time"]
#     cash = strategy_state.get("cash", 1)
#     # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
#     if (williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
#         strategy_state["higher_value"] = candle_stick_indicator.rows['high'][-3]
#     if (williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
#         strategy_state["lower_value"] = candle_stick_indicator.rows['low'][-3]
#     higher_value = strategy_state["higher_value"]
#     open_trades: List[Trade] = []    
#     if higher_value and open > higher_value and cash:
#         trade = Trade.open_trade(
#             slippage=slippage,
#             entry_price=open,
#             cash_to_spend=cash,
#             open_indicators=indicators,
#         )
#         open_trades.append(trade)
#         # note: do not remove the buy signal so we buy many times
#         # strategy_state["higher_value"] = None
#         if "cash" in strategy_state:
#             strategy_state["cash"] = 0
#     return open_trades

# def wf_buy_every_cross_strategy(
#         strategy_state: Dict[str, Any], 
#         indicators: List[Indicator]
#         )->List[Trade]:
#     candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
#     williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
#     open = candle_stick_indicator.cur_step['open']
#     close = candle_stick_indicator.cur_step['close']
#     high = candle_stick_indicator.cur_step['high'] 
#     low = candle_stick_indicator.cur_step['low']
#     time = candle_stick_indicator.cur_step["time"]
#     cash = strategy_state.get("cash", 1)
#     # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
#     if (williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
#         strategy_state["higher_value"] = candle_stick_indicator.rows['high'][-3]
#     if (williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
#         strategy_state["lower_value"] = candle_stick_indicator.rows['low'][-3]
#     higher_value = strategy_state["higher_value"]
#     open_trades: List[Trade] = []    
#     if higher_value and high > higher_value and cash:
#         trade = Trade.open_trade(
#             slippage=slippage,
#             entry_price=higher_value,
#             cash_to_spend=cash,
#             open_indicators=indicators,
#         )
#         open_trades.append(trade)
#         # note: do not remove the buy signal so we buy many times
#         # strategy_state["higher_value"] = None
#         if "cash" in strategy_state:
#             strategy_state["cash"] = 0
#     return open_trades