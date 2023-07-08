import sys
sys.path.insert(0, './src/fetch')
from src.fetch.handler import handler

# Black box tests for fetch function.
# Tests all valid and invalid paths through the function.


# Test case 1 - valid input
def test_fetch_success():
    event = {"body": "{\"company_ticker\": \"AAPL\", \"start_date\": \"1/1/2020\"}"}
    response = handler(event, None)
    print(response)
    assert response["statusCode"] == 200
    assert "data_source" in response["body"]
    assert "dataset_type" in response["body"]
    assert "dataset_id" in response["body"]
    assert "time_object" in response["body"]
    assert "events" in response["body"]


# Test case 2 - malformed input JSON
def test_fetch_malformed_input():
    event = {"body": "{\"company_ticker\": \"AAPL\"}"}  # Missing start_date
    response = handler(event, None)
    assert response["statusCode"] == 400
    assert "malformed" in response["body"]


# Test case 3 - invalid company ticker
def test_fetch_invalid_ticker():
    event = {"body": "{\"company_ticker\": \"INVALID\", \"start_date\": \"1/1/2020\"}"}
    response = handler(event, None)
    assert response["statusCode"] == 400
    assert "No data found" in response["body"]


# Test case 4 - invalid start date, too early
def test_fetch_invalid_date_too_early():
    event = {"body": "{\"company_ticker\": \"INVALID\", \"start_date\": \"1/1/1999\"}"}
    response = handler(event, None)
    assert response["statusCode"] == 400
    assert "out of range" in response["body"]


# Test case 5 - invalid start date, occurs after current date
def test_fetch_invalid_date_too_late():
    event = {"body": "{\"company_ticker\": \"INVALID\", \"start_date\": \"1/1/2040\"}"}
    response = handler(event, None)
    assert response["statusCode"] == 400
    assert "out of range" in response["body"]


# Test case 6 - empty company ticker and start date
def test_fetch_invalid_empty_input():
    event = {"body": "{\"company_ticker\": \"\", \"start_date\": \"\"}"}
    response = handler(event, None)
    assert response["statusCode"] == 400
    assert "does not match format '%d/%m/%Y %z'" in response["body"]


# Test case 7 - no company ticker
    event = {"body": "{\"start_date\": \"\"}"}
    response = handler(event, None)
    assert response["statusCode"] == 400
    assert "malformed" in response["body"]
