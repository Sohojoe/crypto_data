from datetime import datetime, timezone
from typing import Any, Dict, List
from data_manifest import DataManifest
from experiment import Experiment
import pandas as pd
from streaming_stock_indicators import CandleStickIndicator, Indicator, WilliamsFractalsIndicator
from trade import Trade


window_size = 100
data_manifest = DataManifest('data')
product = data_manifest.products[0]
platform = data_manifest.platforms[0]
time_period="3D"
# time_period="12H"
begin = data_manifest.start_time
slippage = 0.005
# begin = datetime(2023, 1, 1).replace(tzinfo=timezone.utc)

indicators=[
            # MovingAverageIndicator(window_size=window_size, lookback_period=10),
            WilliamsFractalsIndicator(window_size=window_size)
            ]

def wf_buy_on_open_strategy(
        strategy_state: Dict[str, Any], 
        indicators: List[Indicator]
        )->List[Trade]:
    candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
    williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
    open = candle_stick_indicator.cur_step['open']
    close = candle_stick_indicator.cur_step['close']
    high = candle_stick_indicator.cur_step['high'] 
    low = candle_stick_indicator.cur_step['low']
    time = candle_stick_indicator.cur_step["time"]
    cash = strategy_state.get("cash", 1)
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    if (williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
        strategy_state["higher_value"] = candle_stick_indicator.rows['high'][-3]
    if (williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
        strategy_state["lower_value"] = candle_stick_indicator.rows['low'][-3]
    higher_value = strategy_state["higher_value"]
    open_trades: List[Trade] = []    
    if higher_value and open > higher_value and cash:
        trade = Trade.open_trade(
            slippage=slippage,
            entry_price=open,
            cash_to_spend=cash,
            open_indicators=indicators,
        )
        open_trades.append(trade)
        # note: buy signal is removed if we buy
        strategy_state["higher_value"] = None
        if "cash" in strategy_state:
            strategy_state["cash"] = 0
    return open_trades


def wf_sell_on_open_strategy(
        strategy_state: Dict[str, Any], 
        indicators: List[Indicator], 
        open_trades: List[Trade], 
        force_close :bool = False
        )->List[Trade]:
    candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
    williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
    open = candle_stick_indicator.cur_step['open']
    close = candle_stick_indicator.cur_step['close']
    high = candle_stick_indicator.cur_step['high'] 
    low = candle_stick_indicator.cur_step['low']
    time = candle_stick_indicator.cur_step["time"]
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    lower_value = strategy_state["lower_value"]
    closed_trades = []
    if (lower_value and open < lower_value) or force_close:
        cash = strategy_state.get("cash", 0)
        for trade in open_trades:
            cash += trade.close(
                open,
                indicators)
            closed_trades.append(trade)
        # note: we do not set lower_value to None as we want it as our stop loss
        # strategy_state["lower_value"] = None
        if "cash" in strategy_state:
            strategy_state["cash"] = cash
    return closed_trades
        

def wf_buy_on_cross_strategy(
        strategy_state: Dict[str, Any], 
        indicators: List[Indicator]
        )->List[Trade]:
    candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
    williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
    open = candle_stick_indicator.cur_step['open']
    close = candle_stick_indicator.cur_step['close']
    high = candle_stick_indicator.cur_step['high'] 
    low = candle_stick_indicator.cur_step['low']
    time = candle_stick_indicator.cur_step["time"]
    cash = strategy_state.get("cash", 1)
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    if (williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
        strategy_state["higher_value"] = candle_stick_indicator.rows['high'][-3]
    if (williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
        strategy_state["lower_value"] = candle_stick_indicator.rows['low'][-3]
    higher_value = strategy_state["higher_value"]
    open_trades: List[Trade] = []    
    if higher_value and high > higher_value and cash:
        trade = Trade.open_trade(
            slippage=slippage,
            entry_price=higher_value,
            cash_to_spend=cash,
            open_indicators=indicators,
        )
        open_trades.append(trade)
        # note: buy signal is removed if we buy
        strategy_state["higher_value"] = None
        if "cash" in strategy_state:
            strategy_state["cash"] = 0
    return open_trades

def wf_sell_on_cross_strategy(
        strategy_state: Dict[str, Any], 
        indicators: List[Indicator], 
        open_trades: List[Trade], 
        force_close :bool = False
        )->List[Trade]:
    candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
    williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
    open = candle_stick_indicator.cur_step['open']
    close = candle_stick_indicator.cur_step['close']
    high = candle_stick_indicator.cur_step['high'] 
    low = candle_stick_indicator.cur_step['low']
    time = candle_stick_indicator.cur_step["time"]
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    lower_value = strategy_state["lower_value"]
    closed_trades = []
    if (lower_value and low < lower_value) or force_close:
        cash = strategy_state.get("cash", 1)
        for trade in open_trades:
            cash += trade.close(
                lower_value,
                indicators)
            closed_trades.append(trade)
        # note: we do not set lower_value to None as we want it as our stop loss
        # strategy_state["lower_value"] = None
        if "cash" in strategy_state:
            strategy_state["cash"] = cash
    return closed_trades

def wf_buy_every_open_strategy(
        strategy_state: Dict[str, Any], 
        indicators: List[Indicator]
        )->List[Trade]:
    candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
    williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
    open = candle_stick_indicator.cur_step['open']
    close = candle_stick_indicator.cur_step['close']
    high = candle_stick_indicator.cur_step['high'] 
    low = candle_stick_indicator.cur_step['low']
    time = candle_stick_indicator.cur_step["time"]
    cash = strategy_state.get("cash", 1)
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    if (williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
        strategy_state["higher_value"] = candle_stick_indicator.rows['high'][-3]
    if (williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
        strategy_state["lower_value"] = candle_stick_indicator.rows['low'][-3]
    higher_value = strategy_state["higher_value"]
    open_trades: List[Trade] = []    
    if higher_value and open > higher_value and cash:
        trade = Trade.open_trade(
            slippage=slippage,
            entry_price=open,
            cash_to_spend=cash,
            open_indicators=indicators,
        )
        open_trades.append(trade)
        # note: do not remove the buy signal so we buy many times
        # strategy_state["higher_value"] = None
        if "cash" in strategy_state:
            strategy_state["cash"] = 0
    return open_trades

def wf_buy_every_cross_strategy(
        strategy_state: Dict[str, Any], 
        indicators: List[Indicator]
        )->List[Trade]:
    candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
    williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
    open = candle_stick_indicator.cur_step['open']
    close = candle_stick_indicator.cur_step['close']
    high = candle_stick_indicator.cur_step['high'] 
    low = candle_stick_indicator.cur_step['low']
    time = candle_stick_indicator.cur_step["time"]
    cash = strategy_state.get("cash", 1)
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    if (williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
        strategy_state["higher_value"] = candle_stick_indicator.rows['high'][-3]
    if (williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
        strategy_state["lower_value"] = candle_stick_indicator.rows['low'][-3]
    higher_value = strategy_state["higher_value"]
    open_trades: List[Trade] = []    
    if higher_value and high > higher_value and cash:
        trade = Trade.open_trade(
            slippage=slippage,
            entry_price=higher_value,
            cash_to_spend=cash,
            open_indicators=indicators,
        )
        open_trades.append(trade)
        # note: do not remove the buy signal so we buy many times
        # strategy_state["higher_value"] = None
        if "cash" in strategy_state:
            strategy_state["cash"] = 0
    return open_trades


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

states = [
    {"cash": 1},
    {},
]

experiments = [
    (buy, sell, begin, state) 
        for buy in buy_strategies 
        for sell in sell_strategies 
        for begin in start_times_to_test
        for state in states]

print(f"experiments: {len(experiments)}")

results = []

def should_plot(trade: Trade):
    return False
    # x = trade.return_percent > 0.3
    # return x

for buy_strategy, sell_strategie, begin, additional_state in experiments:
    strategy_state = {
        "higher_value": None,
        "lower_value": None
    }
    strategy_state.update(additional_state)
    # 8 years
    end_time = begin.replace(year=begin.year+4)
    experment = Experiment(
        product=product,
        platform=platform,
        time_period=time_period,
        begin=begin,
        data_manifest=data_manifest,
        indicators=indicators,
        buy_strategy=buy_strategy,
        sell_strategy=sell_strategie,
        slippage=slippage,
        window_size=window_size,
        strategy_state=strategy_state,
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