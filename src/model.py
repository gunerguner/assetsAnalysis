from dataclasses import dataclass
from datetime import datetime
from typing import Any, TypedDict


@dataclass(frozen=True)
class AssetSpec:
    symbol: str
    name: str
    category_key: str


@dataclass(frozen=True)
class CategorySpec:
    key: str
    display_name: str
    items: list[AssetSpec]


@dataclass(frozen=True)
class AnalysisConfig:
    use_ai: bool
    output_format: str


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


class AnalysisResult(TypedDict):
    basic_analysis: str
    ai_analysis: str | None