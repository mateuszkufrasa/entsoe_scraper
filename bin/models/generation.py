import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from entsoe.exceptions import InvalidBusinessParameterError, NoMatchingDataError
from loguru import logger
from more_itertools import peekable
from requests import HTTPError
from urllib3.exceptions import ReadTimeoutError

from bin.config.Config import Config
from bin.models.db_model import DbModel


class Generation(DbModel.Model):
    __tablename__ = 'ENTSOE_Generation'
    __table_args__ = {"schema": "dbo"}

    id = DbModel.Column('Id', DbModel.Integer, primary_key=True)
    dt = DbModel.Column('Datetime', DbModel.DateTime, nullable=False)
    unit = DbModel.Column('Unit', DbModel.String, nullable=False)
    country = DbModel.Column('Country', DbModel.String, nullable=False)
    code = DbModel.Column('Code', DbModel.String, nullable=False)
    fuel = DbModel.Column('Fuel', DbModel.String, nullable=False)
    generation = DbModel.Column('Generation', DbModel.Integer, nullable=True)


class ActualGeneration:

    @staticmethod
    def get_data(country_code: str, days_back_from: int, days_back_to: int, config: Config) -> list[str]:
        n = datetime.datetime.now() + datetime.timedelta(days=days_back_from)
        n1 = datetime.datetime.now() + datetime.timedelta(days=days_back_to)
        dtss = pd.date_range(start=n, end=n1, freq='D', normalize=True, tz=config.to_zone).tolist()
        it = peekable(iter(dtss))
        lst = []
        # TODO: podzielić na wątki + obsługa wyjątków
        threads = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            for x in it:
                logger.info(f'Pobieranie generacji. strefa: {country_code}, data: {x}.')
                try:
                    threads.append(
                        executor.submit(config.client.query_generation_per_plant, country_code, x, it.peek()))
                    logger.success(f'Pobieranie generacji strefa: {country_code}, data: {x} zakończone sukcesem.')
                except HTTPError:
                    logger.error(f'Brak danych dla {country_code}, data: {x}')
                    return []
                except (InvalidBusinessParameterError, NoMatchingDataError, ReadTimeoutError) as e:
                    logger.error(f'Błąd pobierania: {e}.')
                    print(e)
                    pass
                except StopIteration:
                    pass
            for task in as_completed(threads):
                try:
                    lst.append(task.result())
                except:
                    pass
        return lst
