"""The standard dataframe of all necessary items from each ticker
mentioned in the text file of TradingView."""

"""CREATE DATACLASS HERE ONLY AND IN INPUT_READER, CREATE DICT WITH THIS
DATACLASS, THEN LET OTHER CLASSES ADD IN OTHER VARIABLES INTO THE DATACLASS"""

from dataclasses import dataclass

@dataclass
class StockData:
    """Main dataclass that will be used for each ticker's information.

    Arguments:
        ticker : The ticker of the stock (e.g. '7270')
        name : The name of the stock, which will be obtained through scraping
        current : The price as per starting of the program

        Arguments below are all calculated based on strategy input
        buy : Recommended buying price
        stop : Recommended stop-loss price
        target : Recommended target/selling price

        risk : Amount this trade max can lose
        risk_target : 1:1, first target to clear risk amount

        buyable_quantity : Amount of stocks you can buy
            (risk / (buy - stop))
        total_value : Total value of buyable stock amount
            (buyable_quantity * buy)
        total_profit : Total profit amount you obtain from this trade
            (buyable_quantity * (target - buy))

        Arguments below are all scraped from TradingView
        rsi : Current RSI
        macd : Current MACD
        buy_advice : Current buy rating based on all technicals
    """
    type : str = 'N/A'
    ticker: str = 'N/A'
    name: str = 'N/A'
    current: float = 0.0

    buy: float = 0.0
    stop: float = 0.0
    target: float = 0.0

    risk: float = 0.0
    risk_target: float = 0.0  # 1:1 profit target

    buyable_quantity: float = 0.0
    total_value: float = 0.0
    total_profit: float = 0.0
    risk_reward_ratio: float = 0.0

    rsi: float = 0.0
    macd: float = 0.0
    sma: float = 0.0
    buy_advice: str = 'N/A'

