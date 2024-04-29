import json
from datetime import datetime, timedelta, timezone, time

import pytz
from dateutil.tz import tz
from entsoe import EntsoeRawClient
from loguru import logger
from tzlocal import get_localzone_name


class Config:
    def __init__(self, local_tz=get_localzone_name()):
        try:
            with open('credentials.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.error("Nie znaleziono pliku json.")
        self.client = EntsoeRawClient(api_key=data['api_key'], retry_count=10, retry_delay=10,
                                      timeout=60)
        self.local_tz = local_tz
        self.from_zone = tz.tzutc()
        self.dt_start = datetime(2024, 1, 1, 0, 00, tzinfo=self.from_zone)
        self.dt_stop = Config._default_dt_stop(datetime.now() + timedelta(weeks=4))
        self.server = r'DESKTOP-GU0D16O\MYSQLSERVER1'
        self.dbname = 'ENERGIA-TST'
        self.dblink = f'mssql+pyodbc://{self.server}/{self.dbname}?driver=ODBC+Driver+17+for+SQL+Server'

    @staticmethod
    def _default_dt_stop(dt: datetime) -> datetime:
        d_new = dt.date()
        dt_new = datetime.combine(d_new, time(0, 0))
        dt_utc = dt_new.replace(tzinfo=pytz.UTC)
        return dt_utc
