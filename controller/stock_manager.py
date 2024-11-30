import pandas as pd
from datetime import datetime
from typing import Union, Optional
from vnquant.data.loader import DataLoaderVND, DataLoaderCAFE


class Stock: 
    name: str
    time: str
    open: float
    close: float
    high: float
    low: float
    volume: float
    value_trade: float
    change: float
    change_percent: float

    def __init__(self, name, time, open, close, high, low, volume):
        self.name = name
        self.time = time
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.volume = volume


class StockManager:
    def __init__(self, symbols: Union[str, list], start: Optional[Union[str, datetime]]=None, end: Optional[Union[str, datetime]]=None, data_source: str='CAFE', minimal: bool=True, table_style: str='levels', *arg, **karg):
        self.symbols = symbols
        self.start = start
        self.end = end
        self.data_source = data_source
        self.minimal = minimal
        self.table_style = table_style

    def download(self):
        if str.lower(self.data_source) == 'vnd':
            loader = DataLoaderVND(self.symbols, self.start, self.end)
            stock_data = loader.download()
        else:
            loader = DataLoaderCAFE(self.symbols, self.start, self.end)
            stock_data = loader.download()
        
        if self.minimal:
            if str.lower(self.data_source) == 'vnd':
                stock_data = stock_data[['code', 'high', 'low', 'open', 'close', 'adjust_close', 'volume_match', 'value_match']]
            else:
                stock_data = stock_data[['code', 'high', 'low', 'open', 'close', 'adjust_price', 'volume_match', 'value_match']]
            # Rename columns adjust_close or adjust_price to adjust
            list_columns_names = stock_data.columns.names
            list_tupple_names = stock_data.columns.values
            
            for i, (metric, symbol) in enumerate(list_tupple_names):
                if metric in ['adjust_price', 'adjust_close']:
                    list_tupple_names[i] = ('adjust', symbol)

            stock_data.columns = pd.MultiIndex.from_tuples(
                list_tupple_names,
                names=list_columns_names
            )
        if self.table_style == 'levels':
            return stock_data

        if self.table_style == 'prefix':
            new_column_names = [f'{symbol}_{attribute}' for attribute, symbol in stock_data.columns]
            stock_data.columns = new_column_names
            return stock_data

    def get_stock_data(self):
        stock_data = self.download()
        stock_data_without_date = stock_data.to_dict()
        raw_data = []
        num_stocks = 0
        for key, value in stock_data_without_date.items():
            for k, v in value.items():

                if key[0] == 'code':
                    num_stocks += 1
                    raw_data.append(Stock(key[1], None, None, None, None, None, None))
        index = 0
        for key, value in stock_data_without_date.items():
            for k, v in value.items():
                if index == num_stocks:
                    index = 0
                date = k.strftime('%Y-%m-%d')
                raw_data[index].time = date
                if key[0] == 'open':
                    raw_data[index].open = v
                elif key[0] == 'close':
                    raw_data[index].close = v
                elif key[0] == 'high':
                    raw_data[index].high = v
                elif key[0] == 'low':
                    raw_data[index].low = v
                elif key[0] == 'volume_match':
                    raw_data[index].volume = v

                # Calculate value trade, change and change percent
                if raw_data[index].open is not None and raw_data[index].close is not None and raw_data[index].volume is not None:
                    raw_data[index].value_trade = raw_data[index].close * raw_data[index].volume
                    raw_data[index].change = raw_data[index].close - raw_data[index].open
                    raw_data[index].change_percent = (raw_data[index].change / raw_data[index].open) * 100
                index += 1

        return raw_data
    