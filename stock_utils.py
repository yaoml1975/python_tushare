import pandas as pd
import numpy as np
from typing import List, Dict

class StockUtils:
    @staticmethod
    def calculate_returns(prices: pd.Series, periods: int = 1) -> pd.Series:
        return prices.pct_change(periods=periods)
    
    @staticmethod
    def calculate_moving_average(prices: pd.Series, window: int) -> pd.Series:
        return prices.rolling(window=window).mean()
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))