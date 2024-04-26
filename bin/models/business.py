from entsoe import mappings
from loguru import logger
from sqlalchemy import Column, Integer, String

from bin.models.db_model import DbModel


class Bsn(DbModel.Model):
    __tablename__ = 'ENTSOE_business'
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True)
    code = Column(String)
    type = Column(String)

    def __repr__(self):
        return f"BSN code={self.code}, BSN type={self.src_type}"

    @staticmethod
    def generate() -> list:
        objects_list = []
        logger.debug("Generowanie obiektów BSN")
        for k, v in mappings.BSNTYPE.items():
            item = Bsn(code=k, type=v)
            objects_list.append(item)
        logger.debug(f"Liczba wygenerowanych obiektów: {len(objects_list)}")
        return objects_list
