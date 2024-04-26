import json

from dateutil.tz import tz
from entsoe import EntsoeRawClient
from loguru import logger
from tzlocal import get_localzone_name


class Config:
    # TODO: zmodyfikowac argumenty
    def __init__(self, to_zone=get_localzone_name(), from_zone=tz.tzutc()):
        try:
            with open('credentials.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.error("Nie znaleziono pliku json.")
        self.client = EntsoeRawClient(api_key=data['api_key'], retry_count=10, retry_delay=10,
                                      timeout=60)
        self.to_zone = to_zone
        self.from_zone = from_zone
        self.server = r'DESKTOP-GU0D16O\MYSQLSERVER1'
        self.dbname = 'ENERGIA-TST'
        self.dblink = f'mssql+pyodbc://{self.server}/{self.dbname}?driver=ODBC+Driver+17+for+SQL+Server'
