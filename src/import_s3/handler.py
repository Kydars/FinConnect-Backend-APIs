import sys
sys.path.insert(0, 'package/')

import logging
import datetime as dt
import json
import os
import boto3
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)


#   Retrieves data from the S3 Bucket.
def get_s3_data(company):
    s3 = boto3.client('s3')
    try:
        file_object = s3.get_object(Bucket=os.environ["GLOBAL_S3_NAME"],
                                    Key=f"F12A_ZULU_OHLC_{company.upper()}.json")
        dataset_info = json.loads(file_object["Body"].read().decode('utf-8'))
        return dataset_info
    except Exception as e:
        raise Exception(f"Failed to retrieve the bucket data: {str(e)}")


#   Fetchs and Uploads the JSON file to the S3 Bucket.
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

    company_list = ["GOOGL", "TEAM", "MSFT"]
    details = {
        "username": "username",
        "password": "password",
        "group": "F12A-ZULU"
    }
    token = requests.request("POST", login_url, json=details).json()['token']
    start_date = (dt.datetime.utcnow().date() - dt.timedelta(days=1)).strftime("%d/%m/%Y")

    for company in company_list:
        payload = json.dumps({
            "company_ticker": company,
            "start_date": start_date
        })
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        new_data = requests.request("POST", fetch_url, data=payload, headers=headers).json()
        logger.info(f"new_data: {new_data}")

        start_time = dt.datetime.strptime(new_data['events'][0]['attribute']['date'], "%Y-%m-%d %H:%M:%S.%f")
        logger.info(f"start_time: {start_time}")

        try:
            current_data = get_s3_data(company)
            logger.info(f"current_data: {current_data}")
        except Exception as e:
            logger.info(f"failed to retrieve from bucket: {company}")
            return {
                "statusCode": 400,
                "body": json.dumps({"message": f"Failed to retrieve {company} from the S3 bucket: {str(e)}"}),
            }

        latest_time = dt.datetime.strptime(current_data['events'][-1]['attribute']['date'], "%Y-%m-%d %H:%M:%S.%f")
        logger.info(f"latest_time: {latest_time}")

        if latest_time < start_time:
            logger.info("append company: true")
            current_data['events'].append(new_data['events'][0])
            logger.info(f"appended_data: {current_data}")
            payload = json.dumps(current_data)
            response = requests.request("POST", upload_url, data=payload, headers=headers)
            if response.status_code != 200:
                logger.info(f"failed upload: {company}")
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": f"Failed to upload {company} to the S3 bucket."}),
                }
    logger.info("Successful Upload")
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Successfully updated data for companies into the S3 bucket."}),
    }
