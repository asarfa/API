from datetime import datetime, timedelta, date


class Date:

    @staticmethod
    def datetime_to_timestamp(start: datetime, end: datetime):
        return int(start.timestamp()), int(end.timestamp())

    @staticmethod
    def datetime_to_str(start: datetime, end: datetime):
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    @staticmethod
    def from_business(business_day: int):
        if business_day == 252:
            return 365
        elif business_day == 5:
            return 7
        elif business_day == 20:
            return 31
        else:
            count = int(business_day / 20)
            return count * 40

    @staticmethod
    def nearest_business_day_end(date: datetime.date) -> datetime.date:
        if date.weekday() == 5:
            date = date - timedelta(days=1)
        if date.weekday() == 6:
            date = date - timedelta(days=2)
        return date

    @staticmethod
    def nearest_business_day_start(date: datetime.date) -> datetime.date:
        if date.weekday() == 5:
            date = date - timedelta(days=1)
        if date.weekday() == 6:
            date = date + timedelta(days=1)
        return date
