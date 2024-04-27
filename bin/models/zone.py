from entsoe import Area
from loguru import logger
from sqlalchemy import Column, Integer, String

from bin.models.db_model import DbModel


class Zone(DbModel.Model):
    __tablename__ = 'ENTSOE_zones'
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True)
    zone_name = Column(String)
    code = Column(String)
    meaning = Column(String)
    tz_ = Column(String)

    @staticmethod
    def generate() -> list:
        objects_list = []
        logger.debug("Generowanie obiektów Zone")
        for a in Area:
            item = Zone(zone_name=a.name, code=a.code, meaning=a.meaning, tz_=a.tz)
            objects_list.append(item)
        logger.debug(f"Liczba wygenerowanych obiektów: {len(objects_list)}")
        return objects_list
