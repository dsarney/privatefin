"""Tests for fetching, combining, and persisting stock price data."""

import pandas as pd

from src.engine import data_loader


def test_download_single_ticker_flattens_multiindex(monkeypatch):
    index = pd.date_range("2024-01-01", periods=2)
    multi_columns = pd.MultiIndex.from_tuples(
        [("Open", "AAPL"), ("Close", "AAPL"), ("Volume", "AAPL")]
    )
    raw = pd.DataFrame(
        [[1.0, 2.0, 100], [1.5, 2.5, 110]], index=index, columns=multi_columns
    )

    monkeypatch.setattr(data_loader.yf, "download", lambda *args, **kwargs: raw)

    result = data_loader._download_single_ticker("AAPL", "2024-01-01", "2024-01-03")

    assert list(result.columns) == ["Open", "Close", "Volume"]
    assert len(result) == 2


def test_combine_ticker_frames_averages_common_columns():
    index = pd.date_range("2024-01-01", periods=2)
    frame_a = pd.DataFrame(
        {
            "Open": [10.0, 12.0],
            "Close": [11.0, 13.0],
            "Volume": [100, 120],
        },
        index=index,
    )
    frame_b = pd.DataFrame(
        {
            "Open": [20.0, 22.0],
            "Close": [21.0, 23.0],
            "Volume": [200, 220],
        },
        index=index,
    )

    combined = data_loader._combine_ticker_frames({"GOOG": frame_a, "GOOGL": frame_b})

    assert combined.loc[index[0], "Open"] == 15.0
    assert combined.loc[index[1], "Close"] == 18.0
    assert combined.loc[index[0], "Volume"] == 150.0


def test_download_stock_data_returns_none_when_all_downloads_empty(monkeypatch):
    monkeypatch.setattr(
        data_loader,
        "_download_single_ticker",
        lambda *args, **kwargs: pd.DataFrame(),
    )

    result = data_loader.download_stock_data(
        ["FAKE1", "FAKE2"], "2024-01-01", "2024-01-31", save=False
    )

    assert result is None


def test_download_stock_data_saves_csv_for_multiple_tickers(monkeypatch, tmp_path):
    index = pd.date_range("2024-01-01", periods=3)

    def _fake_download(symbol, *_args, **_kwargs):
        close_start = 100 if symbol == "GOOG" else 200
        return pd.DataFrame(
            {
                "Open": [close_start, close_start + 1, close_start + 2],
                "High": [close_start + 1, close_start + 2, close_start + 3],
                "Low": [close_start - 1, close_start, close_start + 1],
                "Close": [close_start, close_start + 1, close_start + 2],
                "Adj Close": [close_start, close_start + 1, close_start + 2],
                "Volume": [1000, 1100, 1200],
            },
            index=index,
        )

    monkeypatch.setattr(data_loader, "_download_single_ticker", _fake_download)

    result = data_loader.download_stock_data(
        ["GOOG", "GOOGL"],
        "2024-01-01",
        "2024-01-10",
        data_dir=tmp_path,
        save=True,
    )

    assert result is not None
    expected_file = tmp_path / "GOOG_GOOGL_historical.csv"
    assert expected_file.exists()
