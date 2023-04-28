# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import pandas as pd
import numpy as np
import yfinance as yf


class TechnicalIndicators:
    def EMA(self, series, period=14):
        return pd.Series(series).ewm(alpha=1.0/period).mean()

    def ADX(self, tickerdata, period=14, close_flag = "Close"):
        high = tickerdata['High']
        low = tickerdata['Low']
        close = tickerdata[close_flag]

        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        
        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift(1)))
        tr3 = pd.DataFrame(abs(low - close.shift(1)))
        
        frames = [tr1, tr2, tr3]
        tr = pd.concat(frames, axis = 1, join = 'inner').max(axis = 1)
        atr = tr.rolling(period).mean()
        
        plus_di = 100 * (self.EMA(plus_dm) / atr)
        minus_di = abs(100 * (self.EMA(minus_dm) / atr))
        
        dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
        adx = ((dx.shift(1) * (period - 1)) + dx) / period
        adx_smooth = self.EMA(adx)
        
        return adx_smooth
    
    def RSI(self, tickerdata, period=14, close_flag = "Close"):
        close = tickerdata[close_flag]
        
        ret = close.diff()
        up = np.where(ret < 0, 0, ret)
        down = np.where(ret > 0, 0, abs(ret))
        
        up_ewm = self.EMA(up, period)
        down_ewm = self.EMA(down, period)
        
        rs = up_ewm/down_ewm
        rsi = 100 - (100 / (1 + rs))

        rsi_df = pd.DataFrame(rsi)
        rsi_df = rsi_df.rename(columns = {0:'rsi'})
        rsi_df = rsi_df.set_index(close.index)
        rsi_df = rsi_df.dropna()

        return rsi_df[3:]
        

class TickerData(TechnicalIndicators):

    def __init__(self, ticker, interval, period=None, start=None, end=None):
        self.ticker = ticker
        self.period = period
        self.interval = interval
        

    def data(self):
        if self.period:
            data = yf.download(
                                tickers=self.ticker,
                                period=self.period,
                                interval=self.interval
                                )
        elif self.start and self.end:
            data = yf.download(
                                tickers=self.ticker,
                                start=self.start,
                                end=self.end,
                                interval=self.interval
                                )
        else:
            data = pd.DataFrame()
        return data

    def get_technical_indicators(self, data):

        # EMA
        data.loc[:, "EMA"] = self.EMA(data.loc[:, "Close"], period=21)

        # ADX
        data.loc[:, "ADX"] = pd.DataFrame(self.ADX(data, period=14))

        # RSI
        data.loc[:, "RSI"] = self.RSI(data, period=14)

        return data

if __name__ == "__main__":

    ticker = TickerData(ticker="^NSEI", period="10y", interval="1d")
    df = ticker.data()
    df = ticker.get_technical_indicators(df)
    df.to_csv("C:/temp/datacal.csv", index=True)
    print(df)

    
        
        
