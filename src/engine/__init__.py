"""Engine layer for market data and indicators.

Re-export the functions the UI and tests typically import so callers can use
``from src.engine import ...`` without reaching into submodules.
"""

from .data_loader import download_stock_data
from .indicator_engine import (
    compute_macd,
    compute_rsi,
    enrich_with_indicators,
    summarize_latest_indicators,
)
