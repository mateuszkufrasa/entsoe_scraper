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
    def generate() -> list:
        objects_list = []
        logger.debug("Generowanie obiektów ProcessType")
        for k, v in mappings.PSRTYPE_MAPPINGS.items():
            item = ProcessType(code=k, type=v)
            objects_list.append(item)
        logger.debug(f"Liczba wygenerowanych obiektów: {len(objects_list)}")
        return objects_list

    @staticmethod
    def insert_or_update(items: list) -> None:
        logger.info(f"Aktualizacja obiektów ProcessType w bazie")
        try:
            for i in items:
                res = DbModel.session.query(ProcessType).filter(ProcessType.code == i.code).first()
                if res:
                    res.code = i.code
                    res.type = i.type
                    DbModel.session.commit()
                    DbModel.session.flush()
                else:
                    logger.info(f"Nowy rekord: {i}")
                    DbModel.session.merge(i)
                    DbModel.session.commit()
        except Exception as e:
            logger.error(e)