from typing import Self

from entsoe import mappings
from loguru import logger
from sqlalchemy import Column, Integer, String

from bin.models.db_model import DbModel


class MktAgreement(DbModel.Model):
    __tablename__ = 'ENTSOE_mkt_agreements'
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True)
    code = Column(String)
    type = Column(String)

    def __repr__(self):
        return f"MktAgreement code={self.code}, MktAgreement type={self.type}"

    @staticmethod
    def generate() -> list[Self]:
        objects_list = []
        logger.debug("Generowanie obiektów MktAgreement")
        for k, v in mappings.MARKETAGREEMENTTYPE.items():
            item = MktAgreement(code=k, type=v)
            objects_list.append(item)
        logger.debug(f"Liczba wygenerowanych obiektów: {len(objects_list)}")
        return objects_list
