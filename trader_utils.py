import pandas as pd
from typing import List, Dict

class TraderUtils:
    def __init__(self, config):
        self.commission_rate = config['trading']['commission_rate']
        self.tax_rate = config['trading']['tax_rate']
        self.slippage = config['trading']['slippage']
    
    def calculate_trade_cost(self, price: float, shares: int, is_buy: bool) -> float:
        """Calculate total transaction cost including commission and tax"""
        value = price * shares
        commission = value * self.commission_rate
        tax = value * self.tax_rate if not is_buy else 0
        slippage_cost = value * self.slippage
        return commission + tax + slippage_cost
    
    def backtest_strategy(self, signals: pd.DataFrame, prices: pd.DataFrame) -> Dict:
        """Backtest a trading strategy based on signals"""
        positions = pd.DataFrame(index=signals.index).fillna(0)
        portfolio = pd.DataFrame(index=signals.index).fillna(0)
        
        # Implement backtesting logic here
        # ...
        
        return {
            'returns': portfolio['returns'],
            'positions': positions,
            'transactions': []
        }