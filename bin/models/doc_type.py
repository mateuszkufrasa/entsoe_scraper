from entsoe import mappings
from loguru import logger
from sqlalchemy import Column, Integer, String

from bin.models.db_model import DbModel


class DocType(DbModel.Model):
    __tablename__ = 'ENTSOE_doc_types'
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True)
    code = Column(String)
    type = Column(String)

    def __repr__(self):
        return f"DocType code={self.code}, DocType type={self.type}"

    @staticmethod
    def generate() -> list:
        objects_list = []
        logger.debug("Generowanie obiektów DocType")
        for k, v in mappings.PSRTYPE_MAPPINGS.items():
            item = DocType(code=k, type=v)
            objects_list.append(item)
        logger.debug(f"Liczba wygenerowanych obiektów: {len(objects_list)}")
        return objects_list
