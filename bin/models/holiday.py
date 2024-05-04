from typing import Any

import holidays
from dateutil.tz import tz
from loguru import logger
from sqlalchemy import Column, Integer, ForeignKey, Boolean, exists
from sqlalchemy.orm import relationship

from bin.models.calendar import Calendar
from bin.models.country import Country
from bin.models.db_model import DbModel
from bin.models.zone import Zone


class Holiday(DbModel.Model):
    __tablename__ = 'Calendar_holiday'
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey('dbo.ENTSOE_countries.id'))
    zone_id = Column(Integer, ForeignKey('dbo.ENTSOE_zones.id'))
    dt_utc_id = Column(Integer, ForeignKey('dbo.Calendar.id'))
    holiday = Column(Boolean, nullable=False)

    country = relationship('Country', backref='country_id', foreign_keys=[country_id])
    zone = relationship('Zone', backref='zone_id', foreign_keys=[zone_id])
    dt_utc = relationship('Calendar', backref='dt_utc_id', foreign_keys=[dt_utc_id])

    def __repr__(self):
        return f"{self.__class__.__name__} zone_id={self.zone_id}, dt_utc_id={self.dt_utc_id}, holiday={self.holiday}"

    # TODO: multiprocessing
    @staticmethod
    def generate() -> list:
        logger.debug(f"Generowanie obiektów {__class__.__name__}")
        out = []
        stmt = exists().where(Calendar.id == Holiday.dt_utc_id)  # TODO: dodać warunek dot. strefy
        res = DbModel.session.query(Calendar).filter(~stmt).all()
        countries = DbModel.session.query(Country).all()
        if res:
            for c in countries:
                zones = DbModel.session.query(Zone).filter(Zone.country_id == c.id).all()
                if zones:
                    for z in zones:
                        logger.debug(f'Budowanie kalendarza świąt dla strefy {z.zone_name}')
                        for i in res:
                            days_off = holidays.country_holidays(c.iso2, years=i.dt_local.year)
                            if i.dt_utc.astimezone(tz.gettz(z.country.tz_)).date() in days_off.keys():
                                new_item = Holiday(country_id=c.id, zone_id=z.id, dt_utc_id=i.id, holiday=True)
                            else:
                                new_item = Holiday(country_id=c.id, zone_id=z.id, dt_utc_id=i.id, holiday=False)
                            out.append(new_item)
        return out

    @staticmethod
    # TODO: optimize
    def insert_or_update(items: list) -> None:
        logger.info(f"Aktualizacja obiektów {__class__.__name__} w bazie")
        try:
            for i in items:
                res = DbModel.session.query(Holiday).filter(Holiday.zone == i.zone).filter(
                    Holiday.dt_utc == i.dt_utc).first()
                if not res:
                    logger.info(f"Nowy rekord: {i}")
                    DbModel.session.merge(i)
            DbModel.session.commit()
        except Exception as e:
            logger.error(e)
