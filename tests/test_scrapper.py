import pandas as pd
from pytest import raises
from src.fetch.scrapper import get_data_v1, get_data_v2

# Black box tests for scrapper function.
# Tests all valid and invalid paths through the scrapper function.


# Test case 1 - Valid ticker symbol
def test_existing_get_data_success():
    ticker = "AAPL"
    start_date = 946684800  # 1/1/2020
    result = get_data_v1(ticker, start_date)
    assert isinstance(result, pd.DataFrame)
    assert result.index[0].year == 2000
    assert result.index[-1].year <= pd.Timestamp("now").year
    assert result.shape[1] == 6
    assert result.columns.tolist() == [
        "open", "high", "low", "close", "volume", "ticker"]


# Test case 2 - Invalid ticker symbol
def test_existing_get_data_failure():
    ticker = "INVALID"
    start_date = 946684800
    with raises(AssertionError):
        get_data_v1(ticker, start_date)


# Test case 3 - Valid ticker symbol
def test_new_get_data_success():
    ticker = "AAPL"
    start_date = 946684800  # 1/1/2020
    result = get_data_v2(ticker, start_date)
    assert isinstance(result, pd.DataFrame)
    assert result.index[0].year == 2000
    assert result.index[-1].year <= pd.Timestamp("now").year
    assert result.shape[1] == 13
    assert result.columns.tolist() == [
        "open", "high", "low", "close", "volume", "daily_change",
        "daily_return", "weekly_change", "weekly_return", "monthly_change",
        "monthly_return", "rsi", "ticker"]


# Test case 4 - Invalid ticker symbol
def test_new_get_data_failure():
    ticker = "INVALID"
    start_date = 946684800
    with raises(AssertionError):
        get_data_v2(ticker, start_date)
