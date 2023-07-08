"""
Tests for the export functionality in the API
"""

import requests
LOGIN = 'https://afzpve4n13.execute-api.ap-southeast-2.amazonaws.com/login'
EXPORT = 'https://afzpve4n13.execute-api.ap-southeast-2.amazonaws.com/F12A_ZULU/export_s3'

CREDS = {
    "username": "username",
    "password": "password",
    "group": "F12A_ZULU"
}
token = requests.post(LOGIN, json=CREDS).json()['token']
headers = {"Authorization": token}


def test_export_success():
    """
    Tests the API can be successfully called
    """

    json = {
        "query": """{company(companyTicker: \"googl\",
                    start: \"2020-01-01\",
                    end: \"2021-01-01\")
                    {events {attribute {open high low close date}}}}"""
    }

    resp = requests.post(EXPORT, json=json, headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert "company" in data
    assert "events" in data["company"]
    assert bool(data["company"]["events"])
    assert "attribute" in data["company"]["events"][0]
    assert "open" in data["company"]["events"][0]["attribute"]
    assert "high" in data["company"]["events"][0]["attribute"]
    assert "low" in data["company"]["events"][0]["attribute"]
    assert "close" in data["company"]["events"][0]["attribute"]
    assert "date" in data["company"]["events"][0]["attribute"]


def test_stress_test():
    """
    Tests the API can handle heavy requests
    """

    json = {
        "query": """{company(companyTicker: \"aapl\",
                    start: \"1980-01-01\",
                    end: \"2020-01-01\")
                    {events {attribute {date}}}}"""
    }

    resp = requests.post(EXPORT, json=json, headers=headers)

    assert resp.status_code == 200

#     query = '''{company(name: "tsla")}'''
#     response = client.execute(query)
#     # snapshot.assert_match(client.execute('''{company(name: "tsla")}'''))


def test_invalid_ticker():
    """
    Tests the API can handle invalid tickers
    """

    json = {
        "query": """{company(companyTicker: \"INVALID\",
                    start: \"2020-01-01\",
                    end: \"2021-01-01\")
                    {events {attribute {date}}}}"""
    }

    resp = requests.post(EXPORT, json=json, headers=headers)

    assert resp.status_code == 400


def test_time_overlaps():
    """
    Tests the API can handle start times which are after the end time
    """

    json = {
        "query": """{company(companyTicker: \"tsla\",
                    start: \"2021-01-01\",
                    end: \"2020-01-01\")
                    {events {attribute {date}}}}"""
    }

    resp = requests.post(EXPORT, json=json, headers=headers)

    assert resp.status_code == 200
    assert resp.status_code == 200
    data = resp.json()
    assert "company" in data
    assert "events" in data["company"]
    assert not bool(data["company"]["events"])


def test_exclusive_dates():
    """
    Tests the API can handle start times which are on one day as exclusive
    """

    json = {
        "query": """{company(companyTicker: \"amzn\",
                    start: \"2021-01-01\",
                    end: \"2021-01-02\")
                    {events {attribute {date}}}}"""
    }

    resp = requests.post(EXPORT, json=json, headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert "company" in data
    assert "events" in data["company"]
    assert not bool(data["company"]["events"])


def test_same_day():
    """
    Tests the API can handle the same day
    """

    json = {
        "query": """{company(companyTicker: \"msft\",
                    start: \"2021-01-01\",
                    end: \"2021-01-01\")
                    {events {attribute {date}}}}"""
    }

    resp = requests.post(EXPORT, json=json, headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert "company" in data
    assert "events" in data["company"]
    assert not bool(data["company"]["events"])


def test_far_past_start():
    """
    Test the API can handle far back starts calls
    """

    json = {
        "query": """{company(companyTicker: \"team\",
                    start: \"1500-01-01\",
                    end: \"2021-01-01\")
                    {events {attribute {date}}}}"""
    }

    resp = requests.post(EXPORT, json=json, headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert "company" in data
    assert "events" in data["company"]
    assert bool(data["company"]["events"])


def test_far_forward_end():
    """
    Test the API can handle far forward ends calls
    """

    json = {
        "query": """{company(companyTicker: \"meta\",
                    start: \"2000-01-01\",
                    end: \"2500-01-01\")
                    {events {attribute {date}}}}"""
    }

    resp = requests.post(EXPORT, json=json, headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert "company" in data
    assert "events" in data["company"]
    assert bool(data["company"]["events"])


def test_far_past_start_and_end():
    """
    Test the API can handle far back starts calls
    """

    json = {
        "query": """{company(companyTicker: \"team\",
                    start: \"1000-01-01\",
                    end: \"1500-01-01\")
                    {events {attribute {date}}}}"""
    }

    resp = requests.post(EXPORT, json=json, headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert "company" in data
    assert "events" in data["company"]
    assert not bool(data["company"]["events"])


def test_far_forward_start_and_end():
    """
    Test the API can handle far back starts calls
    """

    json = {
        "query": """{company(companyTicker: \"team\",
                    start: \"2500-01-01\",
                    end: \"3000-01-01\")
                    {events {attribute {date}}}}"""
    }

    resp = requests.post(EXPORT, json=json, headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert "company" in data
    assert "events" in data["company"]
    assert not bool(data["company"]["events"])
