from typing import Self

from entsoe import mappings
from loguru import logger
from sqlalchemy import Column, Integer, String

from bin.models.db_model import DbModel


class ProcessType(DbModel.Model):
    __tablename__ = 'ENTSOE_process_types'
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True)
    code = Column(String)
    type = Column(String)

    def __repr__(self):
        return f"ProcessType code={self.code}, ProcessType type={self.type}"

    @staticmethod
    def generate() -> list[Self]:
        objects_list = []
        logger.debug("Generowanie obiektów ProcessType")
        for k, v in mappings.PSRTYPE_MAPPINGS.items():
            item = ProcessType(code=k, type=v)
            objects_list.append(item)
        logger.debug(f"Liczba wygenerowanych obiektów: {len(objects_list)}")
        return objects_list
