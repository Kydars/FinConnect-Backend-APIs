import sys
sys.path.insert(0, 'package/')

import logging
import json
import datetime as dt
from scrapper import get_data


# Default minimum start date, 01/01/2010 and timezone (GMT+0)
DEFAULT_START_DATE = 1262304000
MAX_START_DATE = dt.datetime.combine(dt.datetime.utcnow().date(), dt.time.min).timestamp()
DEFAULT_TIMEZONE = " +0000"


logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Fetch, formats and return all OHLC data from Yahoo finance starting from the given date.
def handler(event, context):
    # Error check for invalid input string
    try:
        data = json.loads(event["body"])
        company_ticker = data["company_ticker"].upper()
        start_date = data["start_date"]
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": f"Input JSON was malformed: {str(e)}"}),
        }

    # Append UTC timezone to date.
    start_date += DEFAULT_TIMEZONE

    # Error check for invalid start_date format.
    try:
        start_date = dt.datetime.strptime(start_date, "%d/%m/%Y %z").timestamp()
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": f"start_date was not of type %d/%m/%Y: {str(e)}"}),
        }

    # Check for a valid start_date (between 1/1/2010 and utc now).
    if start_date < DEFAULT_START_DATE or start_date >= MAX_START_DATE:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "The start_date is out of range (must be between the 1/1/2010 and the current date)"}),
        }

    # Assign file headers
    formatted_json_data = {
        "data_source": "yahoo_finance",
        "dataset_type": "Daily stock price",
        "dataset_id": f"{company_ticker}",  # Change the dataset id
        "time_object": {
            "timestamp": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "timezone": "GMT"
        },
        "events": []
    }

    # Error check for valid company ticker.
    try:
        raw_data = get_data(company_ticker, start_date)
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": f"No data found, symbol ({company_ticker}) may be delisted"}),
        }

    # Convert datetime to readable string.
    raw_data = get_data(company_ticker, start_date)
    raw_data['date'] = raw_data.index.strftime("%Y-%m-%d %H:%M:%S.%f")
    json_data = json.loads(raw_data.to_json(orient='records'))

    # Formmat data with timestamps.
    for i in range(len(json_data)):
        time_obj = {
            "timestamp": json_data[i]['date'],
            "timezone": "GMT",
            "duration": 1,
            "duration_unit": "day"
        }
        event_obj = {
            "time_object": time_obj,
            "event_type": "stock ohlc",
            "attribute": json_data[i]
        }
        formatted_json_data['events'].append(event_obj)

    return {
        "statusCode": 200,
        "body": json.dumps(formatted_json_data),
    }
