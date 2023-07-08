import sys
sys.path.insert(0, "package/")

import json
import logging
from schema import schema

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # Deserialising resquests data.
    query = json.loads(event["body"])["query"]
    logger.info(f"q: {query}")

    try:
        result = schema.execute(query)
        if result.data is None:
            logger.error("Invalid query")
            logger.error(result.errors)
            return {
                "statusCode": 400,
                "body": "No data found. Make sure your query contains valid attributes.",
                "headers": {
                    "Content-Type": "application/json",
                }
            }

        if 'company' in result.data and result.data['company'] is None:
            logger.error("Invalid parameters")
            logger.error(result.errors)
            return {
                "statusCode": 400,
                "body": ("No data found. Make sure your query parameters are correct.\n"
                         "Dates are formatted as YYYY-MM-DD.")
            }

        if 'companyList' in result.data and result.data['companyList'] is None:
            logger.error("Invalid parameters")
            logger.error(result.errors)
            return {
                "statusCode": 404,
                "body": ("Couldn't find company list data. Please try again or contact developers.")
            }
        logger.info("graphql query success")
        return {
            "statusCode": 200,
            "body": json.dumps(result.data),
            "headers": {
                "Content-Type": "application/json",
            },
        }
    except Exception:
        logger.error("schema does not execute")
        return {
            "statusCode": 400,
            "body": "Invalid query. Check the format of your query.",
            "headers": {
                "Content-Type": "application/json",
            },
        }

# def read_company(company):
#     with open(f"code/graphql_export/stock_data/{company}_ohlc.json") as file:
#         json_object = json.load(file)
#     return json_object
