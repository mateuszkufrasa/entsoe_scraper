from entsoe import Area, utils, parsers, mappings
from flask import Flask
from loguru import logger

from bin.config.Config import Config
from bin.models.business import Bsn
from bin.models.db_model import DbModel
from bin.models.doc_status import DocStatus
from bin.models.generation import ActualGeneration
from bin.models.mkt_agreement import MktAgreement
from bin.models.primary_source import Psr
from bin.models.zone import Zone
from bin.parser.GenerationParser import GenerationParser

config: Config = Config()
d = utils.check_new_area_codes()  # TODO: sprawdzenie i aktualizacja bid zone
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config.dblink
DbModel.init_app(app)
logger.add('basic_log.log')

with app.app_context():
    DbModel.create_all()
    # uncomment if need for mappings update
    # primary source types
    psr_types = Psr.generate()
    bsn_types = Bsn.generate()
    mkt_agreeements = MktAgreement.generate()
    doc_statuses = DocStatus.generate()
    # bidding zones
    for a in Area:
        new_zone = Zone(zone_name=a.name, code=a.code, meaning=a.meaning, tz_=a.tz, value=a.value)

        logger.info(f"pobieranie danych: {a.name}...")
        generations = ActualGeneration.get_data(a.name, days_back_from=-5, days_back_to=-2, config=config)
        if generations:
            for i in generations:
                ddd = parsers.parse_generation(i, per_plant=True, include_eic=True)
                ddd.index = ddd.index.tz_convert(tz=config.from_zone)
                ddd.index = ddd.index.tz_convert(tz=config.to_zone)
                t = GenerationParser.to_obj(a.name, ddd)
                DbModel.session.add_all(t)
                # TODO: session.merge()
                DbModel.session.commit()
        else:
            pass
