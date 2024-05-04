from entsoe import Area, utils, parsers
from flask import Flask
from loguru import logger

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
from bin.models.zone import Zone
from bin.models.zone_neighbours import ZoneNeighbours
from bin.parser.GenerationParser import GenerationParser
from bin.utils.db import DbUtils

config: Config = Config()
d = utils.check_new_area_codes()  # TODO: sprawdzenie i aktualizacja bid zone
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config.dblink
DbModel.init_app(app)
logger.add('basic_log.log')

with app.app_context():
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

    #TODO: rearrange holidays: save holiday datetimes for each country
    holidays = Holiday.generate()
    Holiday.insert_or_update(items=holidays)

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
