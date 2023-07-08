# Handler for fetch and upload
import sys
sys.path.insert(0, 'package/')
import os
import logging
import json
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    if os.getenv("ENV"):
        env = os.getenv("ENV")
        logger.info(f"environment: {env}")
        if env == "prod":
            base_url = "https://ai8nyjlwr6.execute-api.ap-southeast-2.amazonaws.com/"
        elif env == "staging":
            base_url = "https://5qmp4gs3ud.execute-api.ap-southeast-2.amazonaws.com/"
        else:
            base_url = "https://afzpve4n13.execute-api.ap-southeast-2.amazonaws.com/"
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid Environment"}),
        }
    login_url = f"{base_url}login"
    fetch_url = f"{base_url}F12A_ZULU/fetch"
    upload_url = f"{base_url}F12A_ZULU/upload_s3"
    details = {
        "username": "username",
        "password": "password",
        "group": "F12A-ZULU"
    }

    token = requests.request("POST", login_url, json=details).json()['token']
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    data = json.loads(event["body"])
    company_ticker = data["company_ticker"].upper()
    start_date = data["start_date"]

    payload = json.dumps({
        "company_ticker": company_ticker,
        "start_date": start_date
    })

    try:
        fetch_response = requests.request("POST", fetch_url, data=payload, headers=headers)
        if fetch_response.status_code != 200:
            raise Exception(fetch_response.json())
        logger.info("Fetch response success")
    except Exception as e:
        logger.error("Fetch request failed")
        return {
            "statusCode": fetch_response.status_code,
            "body": json.dumps(e),
        }

    try:
        upload_response = requests.request("POST", upload_url, json=fetch_response.json(), headers=headers)
        if upload_response.status_code != 200:
            raise Exception(upload_response.json())
        logger.info("Upload request success")
    except Exception as e:
        logger.error("Upload request failed")
        return {
            "statusCode": upload_response.status_code,
            "body": json.dumps(e),
        }
    # return both upload and fetch return
    logger.info("Completed fetch upload")
    return {
        "statusCode": 200,
        "body": json.dumps(fetch_response.json()),
    }
