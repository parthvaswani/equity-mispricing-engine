import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional


class FinancialDataLoader:
    def __init__(self, ticker: str):
        self.ticker_symbol = ticker.upper()
        self.ticker = yf.Ticker(self.ticker_symbol)

    def fetch_market_data(self) -> Dict[str, Any]:
        """
        Fetches real-time price, market cap, and basic metadata.
        """
        info = self.ticker.info
        
        market_cap = info.get("marketCap")
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        company_name = info.get("longName", self.ticker_symbol)
        
        if not market_cap:
            raise ValueError(f"Could not retrieve market cap for ticker: {self.ticker_symbol}")

        return {
            "ticker": self.ticker_symbol,
            "company_name": company_name,
            "market_cap": float(market_cap),
            "current_price": float(current_price) if current_price else None,
        }

    def fetch_balance_sheet_summary(self) -> Dict[str, Optional[float]]:
        try:
            bs = self.ticker.balance_sheet
            if bs.empty:
                return {"stockholders_equity": None, "total_assets": None}
            
            # Extract most recent annual column
            recent_bs = bs.iloc[:, 0]
            
            # Extract items with fallbacks for common line-item names
            equity = recent_bs.get("Stockholders Equity") or recent_bs.get("Total Stockholder Equity")
            assets = recent_bs.get("Total Assets")
            
            return {
                "stockholders_equity": float(equity) if equity is not None else None,
                "total_assets": float(assets) if assets is not None else None,
            }
        except Exception as e:
            print(f"Warning: Could not automatically parse balance sheet for {self.ticker_symbol}: {e}")
            return {"stockholders_equity": None, "total_assets": None}