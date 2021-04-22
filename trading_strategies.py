"""All possible calculations for obtaining the correct entries/exits"""

import trendln
import pandas as pd
import numpy as np

"""For plotting if needed"""
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt


class Strategies:
    def __init__(self, df):
        self.df = df
        self.risk = 20000

        self.raw_stop = None  # Stop without deviation
        self.raw_target = None  # Target without deviation

        self.buy = None
        self.stop = None
        self.target = None
        self.risk_target = None

        self.buyable_quantity = None
        self.total_value = None
        self.total_profit = None
        self.risk_reward_ratio = None

        self.levels = []
        self.support = []
        self.resistance = []

    def plot_technicals(self, df, resistance, support):
        df['Date'] = pd.to_datetime(df.index)
        df['Date'] = df['Date'].apply(mpl_dates.date2num)
        df = df.loc[:, ['Date', 'Open', 'High', 'Low', 'Close']]

        fig, ax = plt.subplots()
        candlestick_ohlc(ax, df.values, width=0.6, \
                         colorup='green', colordown='red', alpha=0.8)
        date_format = mpl_dates.DateFormatter('%d %b %Y')
        ax.xaxis.set_major_formatter(date_format)
        fig.autofmt_xdate()
        fig.tight_layout()

        plt.hlines(resistance[1], xmin=df['Date'][resistance[0]], \
                   xmax=max(df['Date']), colors='blue')

        plt.hlines(support[1], xmin=df['Date'][support[0]], \
                   xmax=max(df['Date']), colors='blue')

        plt.hlines(self.stop, xmin=df['Date'][2], \
                   xmax=max(df['Date']), colors='red')

        plt.hlines(self.target, xmin=df['Date'][1], \
                   xmax=max(df['Date']), colors='green')

        # for res in resistance:
        #     plt.hlines(res[1], xmin=df['Date'][res[0]], \
        #                xmax=max(df['Date']), colors='blue')
        plt.show()

    def calculate_strategy_points(self, stop, target):
        self.buy = round(self.df.iloc[-1]["Close"], 2)

        # IF self.buy is x% close to self.stop, use a different low deviation %

        self.stop = self.needs_adjusted_stop(self.buy, stop) #round((stop * self.max_low_deviation), 2)
        self.target = round((target * self.max_high_deviation), 2)
        self.risk_target = round((self.buy + (self.buy - self.stop)), 2)

        self.buyable_quantity = round((self.risk / (self.buy - self.stop)), 2)
        self.total_value = round((self.buyable_quantity * self.buy), 2)
        self.total_profit = round((self.buyable_quantity * (self.target - self.buy)), 2)
        self.risk_reward_ratio = round(((self.target - self.buy) / (self.buy - self.stop)), 2)

    def needs_adjusted_stop(self, buy, stop):
        higher = 1.02
        lower = 0.98

        deviation = 0.98

        if buy >= stop*higher:
            return round((buy * deviation), 2)
        elif buy*lower <= stop:
            return round((buy * deviation), 2)
        else:
            return round((stop * self.max_low_deviation), 2)


        # First define the raw stop
        # If self.buy is % higher than raw stop
        # True > We need an adjusted stop that overwrite the pre-set deviation

        # elif
        # If self.buy is % close to stop with deviation
        # True > We need an adjusted stop that overwrite the pre-set deviation


class PullbackStrategy(Strategies):
    def __init__(self, df):
        super().__init__(df)
        self.max_low_deviation = 0.98
        self.max_high_deviation = 1.02

        """trendln.calc_support_resistance() returns in [0][1][1] the
        most recent avg. support. [0][1][0] returns the slope. In order
        to get the total avg of the inserted date timeline, calculation is
        [0][1][1] + [0][1][0] * date timeline"""

    def calculate_technicals(self):
        """Use trendln to get the minimas and use the last minima as a stop * deviation.
        If this is to be plotted, add some variables in self for storing the co-ords"""

        low = trendln.calc_support_resistance(self.df["Low"], accuracy=2)
        low = low[0][0][-1]  # [Support][Minimas][Latest minima index]

        high = trendln.calc_support_resistance(self.df["High"], accuracy=4)
        high = high[1][0][-3:]  # [Resistance][Maximas][last 3 maxima index's]

        self.raw_stop = self.df["Low"].iloc[low]
        """###########################################"""
        #self.raw_target = self.df["High"].iloc[high]
        self.raw_target = self._is_highest_pivot(high)
        """^^^^^^Grabs max from latest 4-5 pivots^^^^^^"""

    def plot_technicals(self):
        """Use combination of trendln and also edit plot so that
        stop and target are in it. Probably have to copy the method
        from the library and adjust it."""
        pass


    def _is_highest_pivot(self, pivots):
        latest_pivot = []
        for pivot in pivots:
            latest_pivot.append(self.df["High"].iloc[pivot])

        print(latest_pivot)

        return max(latest_pivot)

class SupportStrategy(Strategies):
    max_low_deviation = 0.985
    max_high_deviation = 1.02

    def calculate_technicals(self):
        for row in range(2, self.df.shape[0] - 2):
            if self.__is_support(self.df, row):
                self.support.append((row, self.df['Low'][row]))  # Take out

                # self.support.append((df.iloc[row].name, df['Low'][row]))
            elif self.__is_resistance(self.df, row):
                self.resistance.append((row, self.df['High'][row]))  # Take out

                # self.resistance.append((df.iloc[row].name, df['Low'][row]))

        self.raw_stop = self.support[-1][1]
        self.raw_target = self.resistance[-1][1]

        """Instead of returning a row value, try and return 
        the date so that the user can confirm whether the supp is ok"""

    def __is_support(self, df, row):
        support = df['Low'][row] < df['Low'][row - 1] and \
                  df['Low'][row] < df['Low'][row + 1] and \
                  df['Low'][row + 1] < df['Low'][row + 2] and \
                  df['Low'][row - 1] < df['Low'][row - 2]

        return support

    def __is_resistance(self, df, row):
        resistance = df['High'][row] > df['High'][row - 1] and \
                     df['High'][row] > df['High'][row + 1] and \
                     df['High'][row + 1] > df['High'][row + 2] and \
                     df['High'][row - 1] > df['High'][row - 2]

        return resistance


class OutbreakStrategy(Strategies):
    max_low_deviation = 0.98
    max_high_deviation = 0.98

    def calculate_technicals(self):
        for row in range(2, self.df.shape[0] - 2):
            if self.__is_support(self.df, row):
                self.support.append((row, self.df['Low'][row]))  # Take out

                # self.support.append((df.iloc[row].name, df['Low'][row]))
            elif self.__is_resistance(self.df, row):
                self.resistance.append((row, self.df['High'][row]))  # Take out

                # self.resistance.append((df.iloc[row].name, df['Low'][row]))

        self.raw_stop = self.df.iloc[-1]["Close"]  # TODO - Buy price
        self.raw_target = (
            self.resistance[-1][1] - self.support[-1][1]
                          ) + self.resistance[-1][1]

        """Instead of returning a row value, try and return 
        the date so that the user can confirm whether the supp is ok"""

    def __is_support(self, df, row):
        support = df['Low'][row] < df['Low'][row - 1] and \
                  df['Low'][row] < df['Low'][row + 1] and \
                  df['Low'][row + 1] < df['Low'][row + 2] and \
                  df['Low'][row - 1] < df['Low'][row - 2]

        return support

    def __is_resistance(self, df, row):
        resistance = df['High'][row] > df['High'][row - 1] and \
                     df['High'][row] > df['High'][row + 1] and \
                     df['High'][row + 1] > df['High'][row + 2] and \
                     df['High'][row - 1] > df['High'][row - 2]

        return resistance

class BottomingStrategy(Strategies):
    max_low_deviation = 1
    max_high_deviation = 1

    def calculate_technicals(self):
        """Use trendln to get the minimas and use the last minima as a stop * deviation.
        If this is to be plotted, add some variables in self for storing the co-ords"""

        low = trendln.calc_support_resistance(self.df["Low"], accuracy=4)
        low = low[0][0][-1]  # [Support][Minimas][Latest minima index]

        high = trendln.calc_support_resistance(self.df["High"], accuracy=4)
        high = high[1][0]  # [Resistance][Maximas]

        self.raw_stop = self.df["Low"].iloc[low]
        self.raw_target = self._is_highest_pivot(high)

    def _is_highest_pivot(self, pivots):
        latest_pivot =[]
        for pivot in pivots:
            latest_pivot.append(self.df["High"].iloc[pivot])

        print(latest_pivot)

        return max(latest_pivot)

class PlainStrategy(Strategies):
    max_low_deviation = 1
    max_high_deviation = 1
    pass

