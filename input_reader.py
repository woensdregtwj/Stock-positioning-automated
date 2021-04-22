"""Reads ticker from a txt file that was extracted from TradingView
and formats it neatly"""
import tkinter as tk
from tkinter import filedialog

import os

from stocks_dataframe import StockData

from ErrorClasses import IncorrectFile, IncorrectData

class TextReader:
    """Reads text file and saves tickers in a list that is reformatted
    so that other classes can easily use the tickers."""
    def __init__(self):
        """"""
        self.root = tk.Tk()
        self.root.withdraw()

        self.ticker_file = self.read_file()
        self.tickers = {}

        #self.format_data(self.ticker_file)

    def read_file(self):
        text_file = filedialog.askopenfile()

        if not os.path.abspath(text_file.name).endswith('.txt'):
            raise IncorrectFile("Only accepts text files from TradingView")

        with open(os.path.abspath(text_file.name), 'r') as file:
            return file.read()

    def format_data(self, data):
        tickers_unformatted = data.split(',')
        tickers_formatted = {}

        active_key = "No Category"

        for item in tickers_unformatted:
            if item.startswith("###"):
                active_key = item
                continue

            tickers_formatted.setdefault(active_key, [])

            if item.startswith("TSE:") and item[4:].isdecimal():
                ticker = StockData(type=active_key, ticker=item[4:])  # Dataclass as dict value
                tickers_formatted[active_key].append(ticker)
            else:
                raise IncorrectData(
                    "Please check data of your text file. It does not align "
                    "with the 'TSE:0000' format."
                )
        return tickers_formatted





