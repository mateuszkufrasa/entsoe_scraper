import multiprocessing
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, time
from multiprocessing import freeze_support

import pandas as pd
import pytz
from entsoe import Area, utils, parsers
from entsoe.decorators import retry
from entsoe.exceptions import NoMatchingDataError
from flask import Flask
from loguru import logger
import dateutil.tz as dtz

from bin.config.Config import Config
from bin.models.business import Bsn
from bin.models.calendar import Calendar
from bin.models.country import Country
from bin.models.db_model import DbModel
from bin.models.doc_status import DocStatus
from bin.models.doc_type import DocType
from bin.models.generation import ActualGeneration
from bin.models.holiday import Holiday
from bin.models.mkt_agreement import MktAgreement
from bin.models.primary_source import Psr
from bin.models.process_type import ProcessType
from bin.models.total_load.tot_load_da_fc import TotalLoadDayAheadForecast
from bin.models.zone import Zone
from bin.models.zone_neighbours import ZoneNeighbours
from bin.parser.GenerationParser import GenerationParser
from bin.utils.datetime_requests import DatetimeRequests
from bin.utils.db import DbUtils

config: Config = Config()
d = utils.check_new_area_codes()  # TODO: sprawdzenie i aktualizacja bid zone
app = Flask(__name__)
app.app_context().push()
app.config["SQLALCHEMY_DATABASE_URI"] = config.dblink
DbModel.init_app(app)
logger.add(sink='basic_log.log')

if __name__ == "__main__":
    with app.app_context() as a:
        DbModel.create_all()

        # insert/update mappings
        psr_types = Psr.generate()
        Psr.insert_or_update(items=psr_types)

        bsn_types = Bsn.generate()
        Bsn.insert_or_update(items=bsn_types)

        mkt_agreeements = MktAgreement.generate()
        MktAgreement.insert_or_update(items=mkt_agreeements)

        doc_statuses = DocStatus.generate()
        DocStatus.insert_or_update(items=doc_statuses)

        doc_types = DocType.generate()
        DocType.insert_or_update(items=doc_types)

        process_types = ProcessType.generate()
        ProcessType.insert_or_update(items=process_types)

        countries = Country.generate()
        Country.insert_or_update(items=countries)

        bid_zones = Zone.generate()
        Zone.insert_or_update(items=bid_zones)

        bid_zones_neighbours = ZoneNeighbours.generate(bid_zones)
        ZoneNeighbours.insert_or_update(items=bid_zones_neighbours)

        dates = Calendar.generate(dt_from=config.dt_start, dt_to=config.dt_stop, tz_name=config.local_tz)
        Calendar.insert_or_update(items=dates)

        countries = DbModel.session.query(Country).all()
        pool = multiprocessing.Pool(multiprocessing.cpu_count()-1)
        logger.debug(f'Liczba procesów: {multiprocessing.cpu_count()-1}')
        res = []
        pool.map(Holiday.generate, (c for c in countries))
        pool.close()
        pool.join()

        # TODO: test na strefach, dla których nie istnieją dane, oznaczyć te, dla których dane nie są dostarczane
        # TODO: do bazy zapisać sesję pobierania: id, datetime, metodę i jej parametry
        # TODO: dla pobierania historycznego: automatyczna walidacja i dobór zakresu, ew. zagregowanie do dób
        # TODO: multithreading
        # TODO: logowanie
        zones = DbModel.session.query(Zone).all()
        tstamp = datetime.now(tz=pytz.timezone(config.local_tz))

        for z in zones:
            start_date = datetime.now() + timedelta(days=1)
            start_date = DatetimeRequests.to_timestamp(dt=start_date, bid_zone=z)

            stop_date = start_date + timedelta(days=2)
            stop_date = DatetimeRequests.to_timestamp(dt=stop_date, bid_zone=z)

            try:
                logger.debug(f"Pobieranie danych total load da fc dl strefy {z.zone_name}")
                total_load_da_fc = config.client.query_load_forecast(country_code=z.code, start=start_date,
                                                                     end=stop_date)
                x = parsers.parse_loads(total_load_da_fc)
            except NoMatchingDataError:
                logger.warning(f"Błąd parsowania strefa {z.zone_name}")
                # TODO: jeśli nie uda się pobrać -> (NoMatchingDataError) zapisz parametry do bazy
                fn_name = config.client.query_load_forecast.__name__
                TotalLoadDayAheadForecast.on_error_save(dt_local=tstamp, method=fn_name, country_code=z.code,
                                                        start=start_date, end=stop_date)
                x = pd.DataFrame()
            if not x.empty:
                tl_da_fc = []
                for idx, item in x.iterrows():
                    tl_da_fc.append(TotalLoadDayAheadForecast.from_df(index_=idx, row=item, bid_zone=z, tstamp=tstamp))
                TotalLoadDayAheadForecast.insert_or_update(items=tl_da_fc)
                print(x)
    # for a in Area:
    #     logger.info(f"pobieranie danych: {a.name}...")
    #     generations = ActualGeneration.get_data(a.name, days_back_from=-5, days_back_to=-2, config=config)
    #     if generations:
    #         for i in generations:
    #             ddd = parsers.parse_generation(i, per_plant=True, include_eic=True)
    #             ddd.index = ddd.index.tz_convert(tz=config.from_zone)
    #             ddd.index = ddd.index.tz_convert(tz=config.local_tz)
    #             t = GenerationParser.to_obj(a.name, ddd)
    #             DbModel.session.add_all(t)
    #             # TODO: session.merge()
    #             DbModel.session.commit()
    #     else:
    #         pass
