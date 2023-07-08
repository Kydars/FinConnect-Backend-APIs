"""Tests for the fetch_upload endpoint"""
import requests
LOGIN = "https://afzpve4n13.execute-api.ap-southeast-2.amazonaws.com/login"
FETCH_UPLOAD = "https://afzpve4n13.execute-api.ap-southeast-2.amazonaws.com/F12A_ZULU/fetch_upload"
FETCH = "https://afzpve4n13.execute-api.ap-southeast-2.amazonaws.com/F12A_ZULU/fetch"
UPLOAD = "https://afzpve4n13.execute-api.ap-southeast-2.amazonaws.com/F12A_ZULU/upload_s3"

CREDS = {
  "username": "username",
  "password": "password",
  "group": "F12A-ZULU"
}
token = requests.post(LOGIN, json=CREDS).json()['token']
headers = {"Authorization": token}


# Tests valid input
def test_fetch_upload_success():
    JSON = {
        "company_ticker": "AAPL",
        "start_date": "01/01/2019"
    }

    response = requests.post(FETCH_UPLOAD, json=(JSON), headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "data_source" in data
    assert "dataset_type" in data
    assert "dataset_id" in data
    assert "time_object" in data
    assert "events" in data

# Test for response to invalid fetch request
# if this test returns an error, it is assumed that for all invalid fetch requests
# it will return an error


def test_invalid_input():
    JSON = {
        "company_ticker": "INVALID",
        "start_date": "1/1/2019"
    }
    response = requests.post(FETCH_UPLOAD, json=(JSON), headers=headers)
    assert response.status_code != 200
    # if fetch fails, upload also fails - returns an error


# Test checks if the handler returns an error response for a valid fetch request but an invalid upload request
# by replicating what the handler does
def test_upload_only_fail():
    JSON = {
        "company_ticker": "AAPL",
        "start_date": "1/1/2019"
    }
    response = requests.post(FETCH, json=(JSON), headers=headers)
    return_values = response.json()

    # remove dataset_id to cause an error when uploading
    remove_dataset_id = return_values.pop("dataset_id", None)
    response_update = requests.post(UPLOAD, json=remove_dataset_id, headers=headers)
    assert response_update.status_code != 200
