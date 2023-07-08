import requests
LOGIN = "https://afzpve4n13.execute-api.ap-southeast-2.amazonaws.com/login"
UPLOAD = "https://afzpve4n13.execute-api.ap-southeast-2.amazonaws.com/F12A_ZULU/upload_s3"
CREDS = {
  "username": "username",
  "password": "password",
  "group": "F12A-ZULU"
}
JSON = {
    "data_source": "datasource_X",
    "dataset_type": "sensor_X",
    "dataset_id": "test",
    "time_object": {
        "timestamp": "2023-02-12 07:52:02.921420",
        "timezone": "GMT+11"
    },
    "events": [
        {
            "time_object": {
                "timestamp": "2019-07-21 13:04:40.3401012",
                "duration": 1,
                "duration_unit": "second",
                "timezone": "GMT+11"
            },
            "event_type": "sensor reading",
            "attribute": {
                "attr1": 36.0,
                "attr2": "abc",
                "attr3": False
            }
        },
        {
            "time_object": {
                "timestamp": "2019-07-22 13:04:40.301022",
                "duration": 1,
                "duration_unit": "second",
                "timezone": "GMT+11"
            },
            "event_type": "sensor reading",
            "attribute": {
                "attr1": 37.0,
                "attr2": "bcd",
                "attr3": True
            }
        }
    ]
}

token = requests.post(LOGIN, json=CREDS).json()['token']
headers = {"Authorization": token}


def test_upload_json_to_s3():
    response = requests.post(UPLOAD, json=(JSON), headers=headers)
    assert response.json()['message'] == "TEST's OHLC has been successfully uploaded to the S3 bucket."
    assert response.status_code == 200


def test_empty_values_and_no_events():
    JSON = {
        "data_source": "",
        "dataset_type": "",
        "dataset_id": "",
        "time_object": {
            "timestamp": "",
            "timezone": ""
        },
        "events": []
    }

    response = requests.post(UPLOAD, json=(JSON), headers=headers)
    assert response.status_code == 200
    print(response.json()['message'])
    assert response.json()['message'] == "'s OHLC has been successfully uploaded to the S3 bucket."


def test_empty_json_input():
    JSON = {}
    response = requests.post(UPLOAD, json=(JSON), headers=headers)
    assert response.status_code != 200


def test_remove_dataset_id():
    new_json = JSON.pop("dataset_id", None)
    response = requests.post(UPLOAD, json=new_json, headers=headers)
    assert response.status_code != 200
