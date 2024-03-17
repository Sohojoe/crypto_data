

### class for the policy/strategy for making trades


from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, List

from streaming_stock_indicators import CandleStickIndicator, Indicator, WilliamsFractalsIndicator
from trade import Trade


# class BuyStrategy(ABC):
#     @abstractmethod
#     def __call__(self, indicators: List[Indicator]
#         )->List[Trade]:
#         pass

# class SellStrategy(ABC):
#     @abstractmethod
#     def __call__(self, 
#         indicators: List[Indicator], 
#         open_trades: List[Trade], 
#         force_close :bool = False
#         )->List[Trade]:
#         pass

@dataclass
class Policy:
    buy_strategy: Callable[['Policy'], None]
    sell_strategy: Callable[['Policy'], None]
    slippage: float
    start_cash: float
    open_trades: List[Trade] = field(default_factory=list)
    closed_trades: List[Trade] = field(default_factory=list)
    candle_stick_indicator: CandleStickIndicator = field(default=None)
    williams_fractals_indicator: WilliamsFractalsIndicator = field(default=None)
    inidactors_for_cur_step: List[Indicator] = field(default_factory=list)
    cash: float = field(init=False)

    def __post_init__(self):
        self.cash = self.start_cash

    def __str__(self):
        return f"{self.buy_strategy.__name__} - {self.sell_strategy.__name__}, {self.slippage}"

    def step(self, indicators: List[Indicator]):
        self.inidactors_for_cur_step = indicators
        self.candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
        self.williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)

        # self.new_open_trades = []
        self.buy_strategy(self)
        self.sell_strategy(self)

    def open_trade(self, entry_price: float, cash_to_spend: float)->bool:
        cash_to_spend = min(cash_to_spend, self.cash)
        if cash_to_spend == 0:
            return False
        trade = Trade.open_trade(
            slippage=self.slippage,
            entry_price=entry_price,
            cash_to_spend=cash_to_spend,
            open_indicators=self.inidactors_for_cur_step,
        )
        self.cash -= cash_to_spend
        self.open_trades.append(trade)
        return True
    
    def close_trade(self, trade: Trade, exit_price: float):
        cash = trade.close(exit_price, self.inidactors_for_cur_step)
        self.cash += cash
        self.open_trades.remove(trade)
        self.closed_trades.append(trade)
        return True
    
    def close_all_trades(self, exit_price: float):
        num_closed = 0
        for trade in self.open_trades.copy():
            trade_close = self.close_trade(trade, exit_price)
            if trade_close:
                num_closed += 1
        return num_closed

    def end(self, indicators: List[Indicator]):
        self.inidactors_for_cur_step = indicators
        self.candle_stick_indicator = next((indicator for indicator in indicators if isinstance(indicator, CandleStickIndicator)), None)
        self.williams_fractals_indicator = next((indicator for indicator in indicators if isinstance(indicator, WilliamsFractalsIndicator)), None)
        self.close_all_trades(self.candle_stick_indicator.cur_step['close'])
