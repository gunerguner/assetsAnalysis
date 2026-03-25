from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict


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


class AnalysisResult(TypedDict):
    basic_analysis: str
    ai_analysis: str | None