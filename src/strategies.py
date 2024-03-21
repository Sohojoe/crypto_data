

from typing import List

from policy import Policy
from streaming_stock_indicators import Indicator
from trade import Trade


def crossed_and_closed_above(indicator_value: float, cur_step: dict)->bool:
    open_is_below = cur_step["open"] < indicator_value
    close_is_above = cur_step["close"] > indicator_value
    return open_is_below and close_is_above

def crossed_and_closed_below(indicator_value: float, cur_step: dict)->bool:
    open_is_above = cur_step["open"] > indicator_value
    close_is_below = cur_step["close"] < indicator_value
    return open_is_above and close_is_below

def crossed_up(indicator_value: float, cur_step: dict)->bool:
    open_is_below = cur_step["open"] < indicator_value
    high_is_above = cur_step["high"] > indicator_value
    return open_is_below and high_is_above

def crossed_down(indicator_value: float, cur_step: dict)->bool:
    open_is_above = cur_step["open"] > indicator_value
    low_is_below = cur_step["low"] < indicator_value
    return open_is_above and low_is_below


def buy_hodl_strategy(self: Policy):
    open = self.candle_stick_indicator.cur_step['open']
    if self.cash:
        self.open_trade(entry_price=open, cash_to_spend=self.cash)

def sell_hodl_strategy(self: Policy):
    return

def wf_buy_on_crossed_and_closed_above_strategy(self: Policy):
    cur_step = self.candle_stick_indicator.cur_step
    if not hasattr(self, 'higher_value'):
        self.higher_value = None
        self.lower_value = None
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    if (self.williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
        self.higher_value = self.candle_stick_indicator.rows['high'][-3]
    if (self.williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
        self.lower_value = self.candle_stick_indicator.rows['low'][-3]

    indicator_value = self.higher_value
    if not indicator_value: return
    if crossed_and_closed_above(indicator_value, cur_step):
        if self.open_trade(entry_price=cur_step["close"], cash_to_spend=self.cash):
            # note: buy signal is removed if we buy
            self.higher_value = None


def wf_sell_on_crossed_and_closed_below_strategy(self: Policy):
    cur_step = self.candle_stick_indicator.cur_step
    indicator_value = self.lower_value
    if not indicator_value: return
    if crossed_and_closed_below(indicator_value, cur_step):
        num_closed = self.close_all_trades(exit_price=cur_step["close"])
        if num_closed:
            # note: we do not set lower_value to None as we want it as our stop loss
            # strategy_state["lower_value"] = None
            pass

def wf_buy_on_crossed_up_strategy(self: Policy):
    cur_step = self.candle_stick_indicator.cur_step
    if not hasattr(self, 'higher_value'):
        self.higher_value = None
        self.lower_value = None
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    if (self.williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
        self.higher_value = self.candle_stick_indicator.rows['high'][-3]
    if (self.williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
        self.lower_value = self.candle_stick_indicator.rows['low'][-3]
    
    indicator_value = self.higher_value
    if not indicator_value: return
    if crossed_up(indicator_value, cur_step):
        if self.open_trade(entry_price=indicator_value, cash_to_spend=self.cash):
            # note: buy signal is removed if we buy
            self.higher_value = None

def wf_sell_on_crossed_down_strategy(self: Policy):
    cur_step = self.candle_stick_indicator.cur_step
    indicator_value = self.lower_value
    if not indicator_value: return
    if crossed_down(indicator_value, cur_step):
        num_closed = self.close_all_trades(exit_price=indicator_value)
        if num_closed:
            # note: we do not set lower_value to None as we want it as our stop loss
            # strategy_state["lower_value"] = None
            pass

def wf_buy_every_crossed_and_closed_above_strategy(self: Policy):
    cur_step = self.candle_stick_indicator.cur_step
    if not hasattr(self, 'higher_value'):
        self.higher_value = None
        self.lower_value = None
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    if (self.williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
        self.higher_value = self.candle_stick_indicator.rows['high'][-3]
    if (self.williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
        self.lower_value = self.candle_stick_indicator.rows['low'][-3]

    indicator_value = self.higher_value
    if not indicator_value: return
    if crossed_and_closed_above(indicator_value, cur_step):
        if self.open_trade(entry_price=cur_step["close"], cash_to_spend=self.cash):
            # note: do not remove the buy signal so we buy many times
            # strategy_state["higher_value"] = None
            pass

def wf_buy_every_crossed_up_strategy(self: Policy):
    cur_step = self.candle_stick_indicator.cur_step
    if not hasattr(self, 'higher_value'):
        self.higher_value = None
        self.lower_value = None
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    if (self.williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
        self.higher_value = self.candle_stick_indicator.rows['high'][-3]
    if (self.williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
        self.lower_value = self.candle_stick_indicator.rows['low'][-3]

    indicator_value = self.higher_value
    if not indicator_value: return
    if crossed_up(indicator_value, cur_step):
        if self.open_trade(entry_price=indicator_value, cash_to_spend=self.cash):
            # note: do not remove the buy signal so we buy many times
            # strategy_state["higher_value"] = None
            pass