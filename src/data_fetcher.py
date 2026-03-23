import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import yfinance as yf


@dataclass
class AssetData:
    symbol: str
    name: str
    category: str
    current_price: float | None
    previous_close: float | None
    change: float | None
    change_percent: float | None
    volume: int | None
    timestamp: datetime
    error: str | None = None
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "name": self.name,
            "category": self.category,
            "current_price": self.current_price,
            "previous_close": self.previous_close,
            "change": self.change,
            "change_percent": self.change_percent,
            "volume": self.volume,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
        }


class AssetDataFetcher:
    def __init__(self, retry_count: int = 3, retry_delay: float = 1.0):
        self.retry_count = retry_count
        self.retry_delay = retry_delay
    
    def fetch_single(self, symbol: str, name: str, category: str) -> AssetData:
        for attempt in range(self.retry_count):
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                current_price = info.get("currentPrice") or info.get("regularMarketPrice")
                previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
                volume = info.get("volume") or info.get("regularMarketVolume")
                
                change = None
                change_percent = None
                if current_price is not None and previous_close is not None:
                    change = current_price - previous_close
                    change_percent = (change / previous_close) * 100
                
                return AssetData(
                    symbol=symbol,
                    name=name,
                    category=category,
                    current_price=current_price,
                    previous_close=previous_close,
                    change=change,
                    change_percent=change_percent,
                    volume=volume,
                    timestamp=datetime.now(),
                )
            except Exception as e:
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
                else:
                    return AssetData(
                        symbol=symbol,
                        name=name,
                        category=category,
                        current_price=None,
                        previous_close=None,
                        change=None,
                        change_percent=None,
                        volume=None,
                        timestamp=datetime.now(),
                        error=str(e),
                    )
        
        return AssetData(
            symbol=symbol,
            name=name,
            category=category,
            current_price=None,
            previous_close=None,
            change=None,
            change_percent=None,
            volume=None,
            timestamp=datetime.now(),
            error="Unknown error after retries",
        )
    
    def fetch_all(self, assets: list[dict[str, str]]) -> list[AssetData]:
        results = []
        for asset in assets:
            data = self.fetch_single(
                symbol=asset["symbol"],
                name=asset["name"],
                category=asset.get("category", "unknown"),
            )
            results.append(data)
        return results
    
    def fetch_by_category(
        self, assets: list[dict[str, str]], category: str
    ) -> list[AssetData]:
        filtered = [a for a in assets if a.get("category") == category]
        return self.fetch_all(filtered)
