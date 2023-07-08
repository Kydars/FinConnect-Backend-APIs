import sys
sys.path.insert(0, 'package/')

import logging
import json
import os
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


# Uploads the JSON file to the S3 Bucket.
def handler(event, context):
    if os.getenv("ENV"):
        LOGGER.info("ENV " + os.getenv("ENV"))

    s3 = boto3.client("s3")
    LOGGER.info(f"event is {event}")
    LOGGER.info(f"body: {event['body']}")
    json_dict = json.loads(event['body'])
    json_data = json.dumps(json_dict).encode('utf-8')

    # # Add Validation
    company_ticker = json_dict['dataset_id'].upper()
    key = f"F12A_ZULU_OHLC_{company_ticker}.json"
    try:
        s3.put_object(Body=json_data, Bucket=os.environ["GLOBAL_S3_NAME"], Key=key)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"{company_ticker}'s OHLC has been successfully uploaded to the S3 bucket."}),
        }
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": f"Failed to upload {company_ticker} to the S3 bucket."}),
        }
