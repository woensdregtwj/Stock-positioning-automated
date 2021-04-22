"""Grabs the OHLC data from the stock and puts it in a dataframe"""

import datetime as dt
import numpy as np
import pandas as pd
import yfinance as yf

import bs4
import requests
import tradingview_ta as tv

from trading_strategies import SupportStrategy, \
    OutbreakStrategy, PullbackStrategy

from ErrorClasses import UnknownTicker, NoScrapingDataFound

class StockDataframe:
    def __init__(self, ticker, days):
        self.ticker = ticker
        self.dataframe = None
        self.days = days
        self.lows = None
        self.highs = None

    def get_dataframe(self):
        #TODO - Error handling for correctly receiving numbers only from arg 'dataframe'
        start_date = dt.datetime.today() - dt.timedelta(days=self.days)
        end_date = dt.datetime.today()

        ticker = yf.Ticker(f"{self.ticker}.T")

        raw_df = ticker.history(
            interval='1d',
            start=start_date,
            end=end_date
        )

        self.dataframe = self._adjust_for_dividend(ticker, raw_df)

        #self.lows = df['Low'].squeeze()
        #self.highs = df['High'].squeeze()

        """trendln.calc_support_resistance() returns in [0][1][1] the
        most recent avg. support. [0][1][0] returns the slope. In order
        to get the total avg of the inserted date timeline, calculation is
        [0][1][1] + [0][1][0] * date timeline"""

    def _adjust_for_dividend(self, ticker, df):
        if not ticker.dividends.empty:
            dividend_info = (ticker.dividends.index[0],
                             ticker.dividends.iloc[0])
            relevant_columns = ["Open", "High", "Low", "Close"]

            for index in df.index:
                if df.loc[index].name < dividend_info[0]:
                    """All prices before the dividend date does not
                    include the dividend, making the price not aligned
                    with the actual prices. Thus, we += dividend price
                    into the OHLC prices."""
                    for column in relevant_columns:
                        df.loc[index, column] += dividend_info[1]

        return df



class StockDataScraper:
    def __init__(self, ticker):
        self.ticker = ticker
        self.url = self.__get_url(ticker)  # Create method for formatting link + error handling
        self.ticker_name = "None"
        self.rsi = "None"
        self.macd = "None"
        self.sma = "None"
        self.recommendation = "None"

    def scrape_data(self):
        res = requests.get(self.url)
        res.raise_for_status()
        scraped_page = bs4.BeautifulSoup(res.text, 'html.parser')

        try:
            self.__page_is_readable(scraped_page)
        except NoScrapingDataFound:
            return

        self.ticker_name = scraped_page.select(
            "div.tv-category-header__title > h1 > div > div"
        )[0].text

        scrape_technicals = tv.TA_Handler(
            symbol=self.ticker,
            screener="japan",
            exchange="TSE",
            interval=tv.Interval.INTERVAL_1_DAY
        )

        analysis = scrape_technicals.get_analysis()

        self.rsi = analysis.indicators["RSI"]
        self.macd = analysis.indicators["MACD.macd"]
        self.sma = analysis.indicators["SMA20"]
        self.recommendation = analysis.summary['RECOMMENDATION']

        # TODO - DONE, NOW IMPLEMENT THIS INTO main.py

    def __get_url(self, ticker):
        if len(ticker) != 4 or not ticker.isdecimal():
            raise UnknownTicker(
                "Ticker format is not correct for creating the proper link "
                "for web-scraping.")
        return f"https://www.tradingview.com/symbols/TSE-{ticker}/technicals/"

    def __page_is_readable(self, page):
        try:
            error_select = page.select(
                "body > div.tv-main > div.tv-content > div > div > h1"
            )[0].text
        except IndexError:
            """page.select returned [], which means there is no error
            message displayed. Continue reading script."""
            return

        if "This isn't the page you're looking for" in error_select:
            raise NoScrapingDataFound(
                f"Tradingview has no page for ticker {self.ticker}")



















