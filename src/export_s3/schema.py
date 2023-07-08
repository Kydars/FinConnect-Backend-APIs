import sys
sys.path.insert(0, "package/")


if True:  # noqa: E402
    from graphene import ObjectType, String, Int, Float, Schema, Field, JSONString, List
    import boto3
    import logging
    import json
    import os
    import datetime as dt


logger = logging.getLogger()
logger.setLevel(logging.INFO)
START_DATE = "2010-01-01 00:00:00"


class Attribute(ObjectType):
    open = Float(required=True)
    high = Float(required=True)
    low = Float(required=True)
    close = Float(required=True)
    volume = Int(required=True)
    daily_change = Float(required=True)
    daily_return = Float(required=True)
    weekly_change = Float(required=True)
    weekly_return = Float(required=True)
    monthly_change = Float(required=True)
    monthly_return = Float(required=True)
    rsi = Float(required=True)
    ticker = String(required=True)
    date = String(required=True)


class TimeObject(ObjectType):
    timestamp = String(required=True)
    timezone = String(required=True)
    duration = Int()
    duration_unit = String()


class Event(ObjectType):
    event_type = String(required=True)
    time_object = Field(TimeObject, required=True)
    attribute = Field(Attribute, required=True)
    all = JSONString()

    def resolve_all(parent, info):
        return {
            "event_type": parent.event_type,
            "time_object": parent.time_object,
            "attribute": parent.attribute
        }


class Dataset(ObjectType):
    dataset_id = String(required=True)
    data_source = String(required=True)
    time_object = Field(TimeObject, required=True)
    events = List(Event, required=True)
    all = JSONString()

    def resolve_all(parent, info):
        return {
            "dataset_id": parent['dataset_id'],
            "data_source": parent['data_source'],
            "time_object": parent['time_object'],
            "events": [Event.resolve_all(e, info="") for e in parent['events']]
        }


class CompanyTicker(ObjectType):
    ticker = String(required=True)


class Query(ObjectType):
    company = Field(Dataset, company_ticker=String(required=True), start=String(), end=String())
    company_attribute = List(Attribute, company_ticker=String(required=True))
    company_events = List(Event, company_ticker=String(required=True))
    company_list = List(CompanyTicker)

    def resolve_company_events(parent, info, company_ticker, start=START_DATE, end=None):
        if start != START_DATE:
            start = start + ' 00:00:00'
        if not validate_date(start):
            raise Exception(f"Invalid start date: {start}")
        if end is None:
            end = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            end = end + ' 00:00:00'
        if not validate_date(end):
            raise Exception(f"Invalid end date: {end}")

        data = get_s3_data(company_ticker)
        temp = []
        for e in data['events']:
            event_date = e['attribute']['date'][:10]
            if event_date < start or event_date > end:
                continue
            temp.append(
                Event(
                    event_type=e['event_type'],
                    time_object=e['time_object'],
                    attribute=e['attribute']
                )
            )
        return temp

    def resolve_company_attribute(parent, info, company_ticker, start=START_DATE, end=None):
        if start != START_DATE:
            start = start + ' 00:00:00'
        if not validate_date(start):
            raise Exception(f"Invalid start date: {start}")
        if end is None:
            end = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            end = end + ' 00:00:00'
        if not validate_date(end):
            raise Exception(f"Invalid end date: {end}")

        data = get_s3_data(company_ticker)
        temp = []
        for e in data['events']:
            event_date = e['attribute']['date'][:10]
            if event_date < start or event_date > end:
                continue
            e_attr = e['attribute']
            temp.append(
                Attribute(
                    open=e_attr['open'],
                    high=e_attr['high'],
                    low=e_attr['low'],
                    close=e_attr['close'],
                    volume=e_attr['volume'],
                    daily_change=e_attr['daily_change'],
                    daily_return=e_attr['daily_return'],
                    weekly_change=e_attr['weekly_change'],
                    weekly_return=e_attr['weekly_return'],
                    monthly_change=e_attr['monthly_change'],
                    monthly_return=e_attr['monthly_return'],
                    rsi=e_attr['rsi'],
                    ticker=e_attr['ticker'],
                    date=e_attr['date']
                )
            )

        return temp

    def resolve_company(parent, info, company_ticker, start=START_DATE, end=None):
        if start != START_DATE:
            start = start + ' 00:00:00'
        if not validate_date(start):
            raise Exception(f"Invalid start date: {start}")
        if end is None:
            end = str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            end = end + ' 00:00:00'
        if not validate_date(end):
            raise Exception(f"Invalid end date: {end}")

        data = get_s3_data(company_ticker)
        temp = []
        for e in data['events']:
            event_date = e['attribute']['date']
            if event_date < start or event_date > end:
                continue
            temp.append(
                Event(
                    event_type=e['event_type'],
                    time_object=e['time_object'],
                    attribute=e['attribute']
                )
            )
        data['events'] = temp
        return data

    def resolve_company_list(parent, info):
        data = get_s3_companies()
        temp = []
        for symbol in data['symbols']:
            temp.append(
                CompanyTicker(
                    ticker=symbol
                )
            )
        return temp


schema = Schema(
    query=Query
)


def validate_date(date):
    try:
        dt.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        logger.info("Valid date")
        return True
    except Exception:
        logger.error(f"Invalid date: {date}")
        return False


def get_s3_data(company):
    if os.getenv("ENV"):
        logger.info(f"ENV {os.getenv}")
    s3 = boto3.client('s3')
    try:
        file_object = s3.get_object(Bucket=os.environ["GLOBAL_S3_NAME"],
                                    Key=f"F12A_ZULU_OHLC_{company.upper()}.json")
        dataset_info = json.loads(file_object["Body"].read().decode('utf-8'))
        logger.info("logger reached dataset_info")
    except Exception as e:
        print(str(e))
        logger.error("logger did not get file_object")
    return dataset_info


def get_s3_companies():
    s3 = boto3.client('s3')
    try:
        file_object = s3.get_object(Bucket=os.environ["GLOBAL_S3_NAME"],
                                    Key="F12A_ZULU_OHLC_COMPANY_LIST.json")
        dataset_info = json.loads(file_object["Body"].read().decode('utf-8'))
        logger.info("logger reached dataset_info")
    except Exception as e:
        logger.error(e)

    return dataset_info
