from entsoe import Area, mappings
from loguru import logger
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.orm import relationship

from bin.models.db_model import DbModel
from bin.models.zone_neighbours import ZoneNeighbours


class Zone(DbModel.Model):
    __tablename__ = 'ENTSOE_zones'
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True)
    zone_name = Column(String)
    code = Column(String)
    meaning = Column(String, nullable=True)
    tz_ = Column(String, nullable=True)

    def __repr__(self):
        return f"Zone zone_name={self.zone_name}, code={self.code}, meaning={self.meaning}, tz={self.tz_}"

    @staticmethod
    def generate() -> list:
        objects_list = []
        logger.debug("Generowanie obiektów Zone")
        for a in Area:
            item = Zone(zone_name=a.name, code=a.code, meaning=a.meaning, tz_=a.tz)
            objects_list.append(item)
        logger.debug(f"Liczba wygenerowanych obiektów: {len(objects_list)}")
        return objects_list

    @staticmethod
    def insert_or_update(items: list) -> None:
        logger.info(f"Aktualizacja obiektów Zone w bazie")
        try:
            for i in items:
                res = DbModel.session.query(Zone).filter(Zone.code == i.code).first()
                if res:
                    res.zone_name = i.zone_name
                    res.code = i.code
                    res.meaning = i.meaning
                    res.tz_ = i.tz_
                    DbModel.session.merge(res)
                    DbModel.session.commit()
                else:
                    logger.info(f"Nowy rekord: {i}")
                    DbModel.session.merge(i)
                    DbModel.session.commit()
        except Exception as e:
            logger.error(e)

    def get_neighbours(self) -> list:
        out = []
        logger.debug(f"Próba znalezienia sąsiadów, strefa {self.zone_name}")
        if self.zone_name in mappings.NEIGHBOURS.keys():
            neighbouring_zones = mappings.NEIGHBOURS.get(self.zone_name)
            for n in neighbouring_zones:
                res = DbModel.session.query(Zone).filter(Zone.zone_name == n).first()
                nzone = ZoneNeighbours(zone_id=self.id, zone_symbol=self.zone_name, neighbour_id=res.id)
                out.append(nzone)
        else:
            logger.warning(f"Brak strefy {self.zone_name} w zbiorze danych")
        return out
