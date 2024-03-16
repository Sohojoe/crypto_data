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
time_period="1D"
begin = data_manifest.start_time
slippage = 0.01
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
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    if (williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
        strategy_state["higher_value"] = candle_stick_indicator.rows['high'][-3]
    if (williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
        strategy_state["lower_value"] = candle_stick_indicator.rows['low'][-3]
    higher_value = strategy_state["higher_value"]
    open_trades: List[Trade] = []    
    if higher_value and open > higher_value:
        trade = Trade.open_trade(
            product=product,
            platform=platform,
            time_period=time_period,
            open_time=candle_stick_indicator.cur_step["time"],
            slippage=slippage,
            entry_price=open,
            cash_to_spend=1,
            open_indicators=indicators,
        )
        open_trades.append(trade)
        # note: buy signal is removed if we buy
        strategy_state["higher_value"] = None
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
        for trade in open_trades:
            trade.close(
                time,
                open,
                indicators)
            closed_trades.append(trade)
        # note: we do not set lower_value to None as we want it as our stop loss
        # strategy_state["lower_value"] = None
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
    # readbale_time = datetime.fromtimestamp(time, tz=timezone.utc)
    if (williams_fractals_indicator.rows['higher_fractal'][-3] > 0):
        strategy_state["higher_value"] = candle_stick_indicator.rows['high'][-3]
    if (williams_fractals_indicator.rows['lower_fractal'][-3] > 0):
        strategy_state["lower_value"] = candle_stick_indicator.rows['low'][-3]
    higher_value = strategy_state["higher_value"]
    open_trades: List[Trade] = []    
    if higher_value and high > higher_value:
        trade = Trade.open_trade(
            product=product,
            platform=platform,
            time_period=time_period,
            open_time=candle_stick_indicator.cur_step["time"],
            slippage=slippage,
            entry_price=higher_value,
            cash_to_spend=1,
            open_indicators=indicators,
        )
        open_trades.append(trade)
        # note: buy signal is removed if we buy
        strategy_state["higher_value"] = None
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
        for trade in open_trades:
            trade.close(
                time,
                lower_value,
                indicators)
            closed_trades.append(trade)
        # note: we do not set lower_value to None as we want it as our stop loss
        # strategy_state["lower_value"] = None
    return closed_trades


experments = [
    (wf_buy_on_open_strategy, wf_sell_on_open_strategy),
    (wf_buy_on_open_strategy, wf_sell_on_cross_strategy),
    (wf_buy_on_cross_strategy, wf_sell_on_open_strategy),
    (wf_buy_on_cross_strategy, wf_sell_on_cross_strategy)
]

results = []

for ex in experments:
    strategy_state = {
        "higher_value": None,
        "lower_value": None
    }
    experment = Experiment(
        product=product,
        platform=platform,
        time_period=time_period,
        begin=begin,
        data_manifest=data_manifest,
        indicators=indicators,
        buy_strategy=ex[0],
        sell_strategy=ex[1],
        slippage=slippage,
        window_size=window_size,
        strategy_state=strategy_state,
        end_time=None)

    print(experment)
    result = experment.run()
    # print(experment)
    results.append(result)

df = pd.DataFrame(results)
pd.options.display.float_format = '{:,.3f}'.format
print(df.to_string())

print("--- end ---")