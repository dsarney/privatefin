"""Retrieve, normalise, combine, and optionally persist market-price data.

This module is the application's only market-data boundary.  It keeps yfinance-specific
column handling out of the indicator engine and returns a predictable OHLCV DataFrame.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pandas as pd
import yfinance as yf


def _download_single_ticker(
    ticker: str, start_date: str, end_date: str
) -> pd.DataFrame:
    """Download one symbol and flatten yfinance's optional MultiIndex columns.

    yfinance treats ``end_date`` as exclusive.  The returned frame is deliberately not
    cleaned beyond its column shape so that upstream data remains auditable.
    """
    df = yf.download(ticker, start=start_date, end=end_date)

    # Recent yfinance versions may return ("Close", "AAPL") even for one ticker.
    # The rest of PrivateFin works with conventional names such as "Close".
    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        df.columns = [
            column[0] if isinstance(column, tuple) else column for column in df.columns
        ]

    return df


def _combine_ticker_frames(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Create one synthetic OHLCV series by averaging aligned ticker frames.

    This supports company choices such as Alphabet, represented by both GOOG and GOOGL.
    The result is a reproducible company-level blend, not the price of a tradable asset.
    """
    # Ticker keys form the outer column level; OHLCV field names form the inner level.
    combined = pd.concat(frames.values(), axis=1, keys=frames.keys())
    summary = pd.DataFrame(index=combined.index)

    # Only include fields actually supplied by yfinance for the selected symbols.
    for column_name in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
        if column_name in combined.columns.get_level_values(1):
            summary[column_name] = combined.xs(column_name, axis=1, level=1).mean(
                axis=1
            )

    return summary.sort_index()


def download_stock_data(
    ticker: str | Sequence[str],
    start_date,
    end_date,
    data_dir: str | Path = "data",
    save: bool = True,
) -> pd.DataFrame | None:
    """Fetch one company selection and optionally save the resulting data as CSV.

    Args:
        ticker: One market symbol or multiple symbols representing one company.
        start_date: First requested date, accepted in the format supported by yfinance.
        end_date: Exclusive end date, accepted in the format supported by yfinance.
        data_dir: Directory used for the reproducibility CSV.
        save: Whether to persist the returned frame.

    Returns:
        A date-sorted OHLCV frame, or ``None`` when every download is empty.
    """
    print(f"Attempting to fetch data for: {ticker}...")

    # Normalising to a list lets the remainder of the function handle one and many
    # symbols through the same code path.
    tickers = [ticker] if isinstance(ticker, str) else list(ticker)
    frames = {
        symbol: _download_single_ticker(symbol, start_date, end_date)
        for symbol in tickers
    }
    # Drop empty downloads so a failed sibling symbol does not poison a blend.
    frames = {symbol: frame for symbol, frame in frames.items() if not frame.empty}

    if not frames:
        print(f"Error: No data found for {ticker}. Check the symbol.")
        return None

    if len(frames) == 1:
        # A single surviving symbol is already a conventional OHLCV frame.
        df = next(iter(frames.values()))
    else:
        df = _combine_ticker_frames(frames)

    if df.empty:
        print(f"Error: No data found for {ticker}. Check the symbol.")
        return None

    if save:
        output_dir = Path(data_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        ticker_name = "_".join(tickers)
        file_path = output_dir / f"{ticker_name}_historical.csv"
        # This records the exact input used for later auditing; the UI does not
        # currently read it as a download cache.
        df.to_csv(file_path)
        print(f"Success! Data saved to {file_path}")

    return df


if __name__ == "__main__":
    # A lightweight manual smoke test when this module is run directly.
    test_ticker = "AAPL"
    download_stock_data(test_ticker, "2020-01-01", "2024-01-01")
