from entsoe import mappings
from loguru import logger
from sqlalchemy import Column, Integer, String

from bin.models.db_model import DbModel


class DocStatus(DbModel.Model):
    __tablename__ = 'ENTSOE_doc_statuses'
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True)
    code = Column(String)
    type = Column(String)

    def __repr__(self):
        return f"DocStatus code={self.code}, DocStatus type={self.type}"

    @staticmethod
    def generate() -> list:
        objects_list = []
        logger.debug("Generowanie obiektów DocStatus")
        for k, v in mappings.PSRTYPE_MAPPINGS.items():
            item = DocStatus(code=k, type=v)
            objects_list.append(item)
        logger.debug(f"Liczba wygenerowanych obiektów: {len(objects_list)}")
        return objects_list
