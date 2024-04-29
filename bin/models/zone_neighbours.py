from loguru import logger
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from bin.models.db_model import DbModel


class ZoneNeighbours(DbModel.Model):
    __tablename__ = 'ENTSOE_zone_neighbours'
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True)
    zone_symbol = Column(String)
    zone_id = Column(Integer, ForeignKey('dbo.ENTSOE_zones.id'))
    neighbour_id = Column(Integer, ForeignKey('dbo.ENTSOE_zones.id'))

    neighbours = relationship('Zone', backref='neighbouring_zones', foreign_keys=[neighbour_id])
    zone_p = relationship('Zone', backref='zone_parent', foreign_keys=[zone_id])

    def __repr__(self):
        return f"ZoneNeighbour: zone_symbol={self.zone_symbol}, zone_id={self.zone_id}, neighbour_id={self.neighbour_id}"

    @staticmethod
    def generate(zones: list) -> list:
        objects_list = []
        logger.debug("Generowanie obiektów ZoneNeighbours")
        for bz in zones:
            bz = DbModel.session.query(bz.__class__).filter(bz.__class__.zone_name == bz.zone_name).first()
            if bz:
                nz = bz.get_neighbours()
                if nz:
                    for n in nz:
                        objects_list.append(n)
        return objects_list

    @staticmethod
    def insert_or_update(items: list) -> None:
        logger.info(f"Aktualizacja obiektów ZoneNeighbours w bazie")
        try:
            for i in items:
                res = DbModel.session.query(ZoneNeighbours).\
                    filter(ZoneNeighbours.zone_id == i.zone_id).\
                    filter(ZoneNeighbours.neighbour_id == i.neighbour_id).first()
                if res:
                    res.zone_symbol = i.zone_symbol
                    res.zone_id = i.zone_id
                    res.neighbour_id = i.neighbour_id
                    DbModel.session.merge(res)
                    DbModel.session.commit()
                else:
                    logger.info(f"Nowy rekord: {i}")
                    DbModel.session.merge(i)
                    DbModel.session.commit()
        except Exception as e:
            logger.error(e)
