from input_reader import TextReader
from stock_data_reader import StockDataframe, StockDataScraper

from trading_strategies import \
    PullbackStrategy, SupportStrategy, OutbreakStrategy, BottomingStrategy

from file_output import FileOutputter

import pprint
import pandas as pd


class EasyMoneyMaker:
    def __init__(self, days):
        self.stocks_data = None
        # self.strategy = strategy  # 'Pullback', 'Support', 'Outbreak'
        self.days = days  # Stays as seperate variable for if we want further additions

    def initiate(self):
        self.stocks_data = self.read_watchlist()

        for key in self.stocks_data.keys():
            for stock in self.stocks_data[key]:
                # TODO - Doing this one by one is a bit slow, set up multithread
                # print(stock.ticker)
                stock_dataframe = StockDataframe(
                    ticker=stock.ticker, days=self.days)
                stock_dataframe.get_dataframe()
                # print(stock_dataframe.dataframe)

                strategy_output = self.__read_strategy(
                    key, stock_dataframe.dataframe
                )

                scraped_technicals = self.__scrape_indicators(stock.ticker)

                self.__add_to_dataframe(
                    strategy_class=strategy_output,
                    scraper_class=scraped_technicals,
                    stock_dataclass=stock
                )

                print(f"{stock}")
                #strategy_output.plot_technicals(stock_dataframe.dataframe)

        self.__print_data(self.stocks_data)
        # output_data = FileOutputter(self.stocks_data)
        # output_data.output_data()

    def __print_data(self, stocks_data):
        stock_data_list = [
            stock.__dict__ for stock_list in stocks_data.values() \
            for stock in stock_list
        ]
        df = pd.DataFrame(stock_data_list)
        print(df.all)

    def __read_strategy(self, key, dataframe):
        strategy_output = self._select_strategy(key,
                                                dataframe)

        strategy_output.calculate_technicals()
        strategy_output.calculate_strategy_points(
            strategy_output.raw_stop,
            strategy_output.raw_target
        )

        return strategy_output

    def __scrape_indicators(self, ticker):
        scraper = StockDataScraper(ticker)
        scraper.scrape_data()

        return scraper

    def __add_to_dataframe(
            self, strategy_class, scraper_class, stock_dataclass
    ):
        stock_dataclass.buy = strategy_class.buy
        stock_dataclass.buy_advice = strategy_class.buy
        stock_dataclass.current = strategy_class.buy
        stock_dataclass.stop = strategy_class.stop
        stock_dataclass.target = strategy_class.target
        stock_dataclass.risk = strategy_class.risk
        stock_dataclass.risk_target = strategy_class.risk_target
        stock_dataclass.buyable_quantity = strategy_class.buyable_quantity
        stock_dataclass.total_value = strategy_class.total_value
        stock_dataclass.total_profit = strategy_class.total_profit
        stock_dataclass.risk_reward_ratio = strategy_class.risk_reward_ratio

        stock_dataclass.name = scraper_class.ticker_name
        stock_dataclass.rsi = scraper_class.rsi
        stock_dataclass.macd = scraper_class.macd
        stock_dataclass.sma = scraper_class.sma
        stock_dataclass.buy_advice = scraper_class.recommendation

    def read_watchlist(self):
        watchlist = TextReader()
        watchlist.read_file()
        return watchlist.format_data(watchlist.ticker_file)
        print(self.stocks_data)

    def read_dataframe(self):
        for key in self.stocks_data.keys():
            for stock in self.stocks_data[key]:
                # TODO - Doing this one by one is a bit slow, set up multithread
                print(stock.ticker)
                stock_dataframe = StockDataframe(ticker=stock.ticker, days=self.days)
                stock_dataframe.get_dataframe()
                print(stock_dataframe.dataframe)

                strategy_output = self._select_strategy(self.strategy,
                                                        stock_dataframe.dataframe)
                strategy_output.calculate_technicals()

                strategy_output.calculate_strategy_points(
                    strategy_output.raw_stop,
                    strategy_output.raw_target
                )

                stock.buy = strategy_output.buy
                stock.buy_advice = strategy_output.buy
                stock.current = strategy_output.buy
                stock.stop = strategy_output.stop
                stock.target = strategy_output.target
                stock.risk = strategy_output.risk
                stock.risk_target = strategy_output.risk_target
                stock.buyable_quantity = strategy_output.buyable_quantity
                stock.total_value = strategy_output.total_value
                stock.total_profit = strategy_output.total_profit
                stock.risk_reward_ratio = strategy_output.risk_reward_ratio

                print(stock)
                # strategy_output.plot_technicals(stock_dataframe.dataframe,
                #                                 strategy_output.resistance[-1],
                #                                 strategy_output.support[-1])

    def _select_strategy(self, strategy, df):
        current_strategies = {
            '###PULLBACK': PullbackStrategy,
            '###SUPPORT': SupportStrategy,
            '###OUTBREAK': OutbreakStrategy,
            '###BOTTOM': BottomingStrategy
        }
        try:
            return current_strategies[strategy](df)
        except:
            pass  # Find out what exception this is


if __name__ == '__main__':
    stock_data = EasyMoneyMaker(
        90
    )
    stock_data.initiate()

"""
- Start input reader
- Create variable with formatted tickers from input reader
    and this will be the main data structure for adding data
- Start stocks_dataframe and create a dataframe
- With that dataframe we will use trading_strategies for getting
    the correct buy, stop, target etc..
- Also do the additional calculations necessarry for filling the dataclass
- Add all this data back into main datastructure
- Call tradingview_scraper and get the remaining data
- Use the main datastructure for creating an output file


"""
