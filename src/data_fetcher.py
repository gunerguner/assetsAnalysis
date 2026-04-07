import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any

import yfinance as yf

from src.config import AssetSpec
from src.model import AssetData


class AssetDataFetcher:
    def __init__(
        self,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        max_workers: int = 8,
    ):
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.max_workers = max_workers

    def _extract_market_data(
        self, ticker: yf.Ticker, interval: str = "daily"
    ) -> tuple[float | None, float | None, int | None]:
        current_price = None
        previous_close = None
        volume = None

        if interval == "weekly":
            # 周维度：获取周K线数据
            try:
                hist = ticker.history(period="2wk", interval="1wk")
                if hist is not None and len(hist) >= 2:
                    # 最近两周的数据
                    current_week = hist.iloc[-1]
                    previous_week = hist.iloc[-2]
                    current_price = current_week["Close"]
                    previous_close = previous_week["Close"]
                    volume = int(current_week["Volume"]) if "Volume" in current_week else None
            except Exception:
                pass
        else:
            # 日维度：保持原有逻辑
            try:
                fast_info = ticker.fast_info
                current_price = fast_info.get("last_price")
                previous_close = fast_info.get("previous_close")
                volume = fast_info.get("last_volume")
            except Exception:
                pass

            if current_price is None or previous_close is None:
                info = ticker.info
                if current_price is None:
                    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
                if previous_close is None:
                    previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
                if volume is None:
                    volume = info.get("volume") or info.get("regularMarketVolume")

        return current_price, previous_close, volume

    def _create_asset_data(
        self,
        symbol: str,
        name: str,
        category: str,
        current_price: float | None,
        previous_close: float | None,
        volume: int | None,
        error: str | None = None,
    ) -> AssetData:
        change = None
        change_percent = None
        if current_price is not None and previous_close is not None and previous_close != 0:
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
            error=error,
        )

    def fetch_single(self, symbol: str, name: str, category: str, interval: str = "daily") -> AssetData:
        for attempt in range(self.retry_count):
            try:
                ticker = yf.Ticker(symbol)
                current_price, previous_close, volume = self._extract_market_data(ticker, interval)
                return self._create_asset_data(
                    symbol, name, category, current_price, previous_close, volume
                )
            except Exception as e:
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay * (2**attempt) + random.uniform(0, self.retry_delay * 0.3))
                else:
                    return self._create_asset_data(
                        symbol, name, category, None, None, None, error=str(e)
                    )
        return self._create_asset_data(symbol, name, category, None, None, None, error="Unknown error after retries")

    def fetch_all(self, assets: list[AssetSpec], interval: str = "daily") -> list[AssetData]:
        if not assets:
            return []

        results: list[AssetData | None] = [None] * len(assets)
        worker_count = min(self.max_workers, len(assets))

        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            future_to_index = {
                executor.submit(
                    self.fetch_single,
                    symbol=asset.symbol,
                    name=asset.name,
                    category=asset.category_key,
                    interval=interval,
                ): idx
                for idx, asset in enumerate(assets)
            }

            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                results[idx] = future.result()

        return [result for result in results if result is not None]

    def fetch_by_category(self, assets: list[AssetSpec], category: str) -> list[AssetData]:
        filtered = [a for a in assets if a.category_key == category]
        return self.fetch_all(filtered)
