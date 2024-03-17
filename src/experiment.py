from typing import List
import numpy as np
import pandas as pd
from policy import Policy
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
            policy: Policy,
            window_size = 100,
            end_time=None):
        self.product = product
        self.platform = platform
        self.time_period = time_period
        self.begin = begin
        self.data_manifest = data_manifest
        self.policy = policy
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
            policy_str = str(self.policy)
            return (
                f"{policy_str}, "
                f"{self.product}, "
                f"{self.platform}, "
                f"{self.time_period}, "
                f"{self.begin.date()}"
                f"{' to ' + str(self.end_time.date()) if self.end_time is not None else ''}"
            )
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
        
            self.policy.step(indicators)

        # close any open trades        
        self.policy.end(indicators)

        closed_trades = self.policy.closed_trades
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
            "roi": ((self.policy.cash / self.policy.start_cash) - 1.0)*100.,
            # "roi": total_return_percent,
            # "hold_roi": buy_and_hold_return_percent,
            # "vs_hodl": total_return_percent/buy_and_hold_return_percent,
            "buy_strat": self.policy.buy_strategy.__name__.replace('_strategy', ''),
            "sell_strat": self.policy.sell_strategy.__name__.replace('_strategy', ''),
            "expected_ret": expected_return * 100.,
            "std_dev": std_dev_returns * 100.,
            "prob_profit": prob_profit * 100.,
            "trades": len(closed_trades),
            "winning": len([x.return_percent for x in closed_trades if x.return_percent > 0]),
            "loosing": len([x.return_percent for x in closed_trades if x.return_percent < 0]),
            "median_ret": median_return * 100.,
            # "profit_factor": profit_factor,
            # "prob_loss": prob_loss * 100.,
            # "avg_win": avg_win * 100.,
            # "avg_loss": avg_loss * 100.,
            "time_period": self.time_period,
            "slippage": self.policy.slippage,
            "product": self.product,
            "platform": self.platform,
            "start_time": self.begin.date(),
            "end_cash": self.policy.cash,
            }
        if self.end_time is not None:
            self.results['end_time'] = self.end_time.date()
        
        self.closed_trades = closed_trades
        return self.results
    
    def plot(self, should_plot = None):
        for trade in self.closed_trades:
            if should_plot and not should_plot(trade):
                continue
            visualize_indicators = VisualizeIndicators()
            visualize_indicators.visualize_trade(trade)