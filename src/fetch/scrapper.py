import sys
sys.path.insert(0, 'package/')

import requests
import pandas as pd
import datetime as dt
from flagbase import FlagbaseClient, Config, Identity

#   Capture data from a month earlier in order to evaluate monthly change.
MONTHLY_OFFSET = 2629743

# Setup Flagbase Client and user
client = FlagbaseClient(
    config=Config(
        server_key="sdk-server_c52da7a9-185a-4837-85ce-a5b1a5d7a2c4",
    )
)
user = Identity("user", {"user": "true"})


#   Build the url and queries for the financial data starting from 1st of Jan, 2000.
def build_url(ticker, start_date):
    base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"
    site = base_url + ticker
    params = {"period1": int(start_date), "period2": int(dt.datetime.utcnow().timestamp()),
              "interval": "1d", "events": "div,splits"}
    return site, params


#   Downloads historical stock price data into a pandas data frame.
#   @param: ticker - ticker of the company to be scrapped
def get_data(ticker, start_date):
    show = client.variation("improved-fetch-transformation", user, "treatment")

    # If feature turned on, include new data in transformation.
    if show == "treatment":
        return get_data_v2(ticker, start_date)
    else:
        return get_data_v1(ticker, start_date)


#   Existing version of get_data.
def get_data_v1(ticker, start_date):
    # Build URL and assign params
    site, params = build_url(ticker, start_date)

    # Headers to mimic a browser
    headers = {'User-Agent':
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 \
                (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    # Query Yahoo Finance for data.
    response = requests.get(site, params=params, headers=headers)
    if not response.ok:
        raise AssertionError(response.json())
    data = response.json()

    # Convert data into a pandas dataframe.
    frame = pd.DataFrame(data["chart"]["result"][0]["indicators"]["quote"][0])
    temp_time = data["chart"]["result"][0]["timestamp"]

    # Get timestamp data as datetime object to index frame.
    frame.index = pd.to_datetime(temp_time, unit="s")

    # Extract to readable columns.
    frame = frame[["open", "high", "low", "close", "volume"]]

    # Add Ticker to the frame.
    frame['ticker'] = ticker.upper()

    return frame


#   New version of get_data.
def get_data_v2(ticker, start_date):
    # Build URL and assign params
    site, params = build_url(ticker, start_date - MONTHLY_OFFSET)

    # Headers to mimic a browser
    headers = {'User-Agent':
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 \
               (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    # Query Yahoo Finance for data.
    response = requests.get(site, params=params, headers=headers)
    if not response.ok:
        raise AssertionError(response.json())
    data = response.json()

    # Convert data into a pandas dataframe.
    frame = pd.DataFrame(data["chart"]["result"][0]["indicators"]["quote"][0])
    temp_time = data["chart"]["result"][0]["timestamp"]

    # Get timestamp data as datetime object to index frame.
    frame.index = pd.to_datetime(temp_time, unit="s")

    # Extract to readable columns.
    frame = frame[["open", "high", "low", "close", "volume"]]

    # Add daily change
    frame['daily_change'] = frame['close'].diff()

    # Add daily return
    frame['daily_return'] = frame['close'].pct_change()

    # Add weekly change
    frame['weekly_change'] = frame['close'].diff(5)

    # Add weekly return
    frame['weekly_return'] = frame['close'].pct_change(periods=5)

    # Add monthly change
    frame['monthly_change'] = frame['close'].diff(20)

    # Add monthly return
    frame['monthly_return'] = frame['close'].pct_change(periods=20)

    # Calculate RSI
    delta = frame['daily_change']
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # Add RSI to the frame.
    frame['rsi'] = rsi

    # Add Ticker to the frame.
    frame["ticker"] = ticker.upper()

    # Drop any rows with a date earlier than the start_date
    frame = frame.loc[frame.index >= dt.datetime.fromtimestamp(start_date)]

    return frame
