from typing import List
import numpy as np
import pandas as pd
from streaming_stock_indicators import CandleStickIndicator, Indicator, StreamingStockIndicators, WilliamsFractalsIndicator
from trade import Trade
from visualize_indicators import VisualizeIndicators


class Experiment():
    def __init__(
            self,
            product,
            platform,
            time_period,
            begin,
            data_manifest,
            indicators: List[Indicator],
            buy_strategy,
            sell_strategy,
            slippage, 
            window_size = 100,
            end_time=None):
        self.product = product
        self.platform = platform
        self.time_period = time_period
        self.begin = begin
        self.data_manifest = data_manifest
        self.buy_strategy = buy_strategy
        self.sell_strategy = sell_strategy
        self.slippage = slippage
        self.end_time = end_time
        self.results = None

        streaming_stock_indicators = StreamingStockIndicators(data_manifest, window_size=window_size)
        data_generator = streaming_stock_indicators.stream_data_and_window(
            begin, 
            product, 
            platform, 
            time_period, 
            indicators=indicators,
            end_time=end_time)
        self.data_iter = iter(data_generator)

    def __str__(self):
        if self.results is None:
            return f"product: {self.product}, platform: {self.platform}, time_period: {self.time_period}, slippage: {self.slippage}"
        else:
            df = pd.DataFrame([self.results])
            pd.options.display.float_format = '{:,.3f}'.format
            return df.to_string()            

    def run(self):
        open_trades: List[Trade] = []
        closed_trades: List[Trade] = []        
        # df = Trade.create_emptpy_dataframe()

        indicators = None
        while True:
            try:
                indicators = next(self.data_iter)
                candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
                # williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
            except StopIteration:
                break
        
            new_open_trades = self.buy_strategy(indicators)
            open_trades.extend(new_open_trades)
            new_closed_trades = self.sell_strategy(indicators, open_trades)
            closed_trades.extend(new_closed_trades)
            open_trades = [trade for trade in open_trades if trade not in new_closed_trades]

        # close any open trades        
        new_closed_trades = self.sell_strategy(indicators, open_trades, force_close=True)
        closed_trades.extend(new_closed_trades)
        open_trades = [trade for trade in open_trades if trade not in new_closed_trades]

        return_percentages = [x.return_percent for x in closed_trades]
        expected_return = np.mean(return_percentages)
        prob_profit = (len([x for x in return_percentages if x > 0]) / len(return_percentages))
        prob_loss = (len([x for x in return_percentages if x < 0]) / len(return_percentages))
        avg_win = np.mean([x for x in return_percentages if x > 0])
        avg_loss = np.mean([x for x in return_percentages if x < 0])
        # Calculate Profit Factor
        winning_trades = [x for x in return_percentages if x > 0]
        losing_trades = [x for x in return_percentages if x < 0]
        profit_factor = sum(winning_trades) / abs(sum(losing_trades))

        # Calculate Expectancy
        # win_rate = len(winning_trades) / len(return_percentages)
        # loss_rate = len(losing_trades) / len(return_percentages)
        # expectancy = (win_rate * avg_win) - (loss_rate * abs(avg_loss))

        # Calculate Median Return
        median_return = np.median(return_percentages)

        # Calculate Standard Deviation of Returns
        std_dev_returns = np.std(return_percentages)

        # Calculate Win/Loss Ratio
        # win_loss_ratio = len(winning_trades) / len(losing_trades)        

        self.results = {
            # "roi": total_return_percent,
            # "hold_roi": buy_and_hold_return_percent,
            # "vs_hodl": total_return_percent/buy_and_hold_return_percent,
            "expected_return": expected_return * 100.,
            "std_dev_returns": std_dev_returns * 100.,
            "prob_profit": prob_profit * 100.,
            "trades": len(closed_trades),
            "winning": len([x.return_percent for x in closed_trades if x.return_percent > 0]),
            "loosing": len([x.return_percent for x in closed_trades if x.return_percent < 0]),
            "median_return": median_return * 100.,
            "profit_factor": profit_factor,
            # "prob_loss": prob_loss * 100.,
            "avg_win": avg_win * 100.,
            "avg_loss": avg_loss * 100.,
            "time_period": self.time_period,
            "slippage": self.slippage,
            "product": self.product,
            "platform": self.platform,
            }
        
        self.closed_trades = closed_trades
        return self.results
    
    def plot(self):
        for trade in self.closed_trades:
            visualize_indicators = VisualizeIndicators()
            visualize_indicators.visualize_trade(trade)