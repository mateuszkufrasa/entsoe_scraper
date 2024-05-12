import os

import holidays
from dateutil.tz import tz
from loguru import logger
from sqlalchemy import Column, Integer, ForeignKey, exists
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
    dt_utc_id = Column(Integer, ForeignKey('dbo.Calendar.id'))

    country = relationship('Country', backref='country_id', foreign_keys=[country_id])
    dt_utc = relationship('Calendar', backref='dt_utc_id', foreign_keys=[dt_utc_id])

    def __repr__(self):
        return f"{self.__class__.__name__}, country_id={self.country_id}, dt_utc_id={self.dt_utc_id}"

    @staticmethod
    def generate(c) -> None:
        logger.debug(f"Generowanie obiektów {__class__.__name__}", flush=True)
        out = []
        stmt = exists().where(Calendar.id == Holiday.dt_utc_id, Country.id == Holiday.country_id)
        res = DbModel.session.query(Calendar).filter(~stmt).all()
        zones = DbModel.session.query(Zone).filter(Zone.country_id == c.id).all()
        if zones:
            for z in zones:
                logger.debug(f'Budowanie kalendarza świąt dla strefy {z.zone_name}; Process ID={os.getpid()}')
                for i in res:
                    days_off = holidays.country_holidays(c.iso2, years=i.dt_local.year)
                    if i.dt_utc.astimezone(tz.gettz(z.country.tz_)).date() in days_off.keys():
                        new_item = Holiday(country_id=c.id, dt_utc_id=i.id)
                        out.append(new_item)
        Holiday.insert_or_update(out)

    @staticmethod
    # TODO: optimize
    def insert_or_update(items: list) -> None:
        logger.info(f"Aktualizacja obiektów {__class__.__name__} w bazie")
        try:
            for i in items:
                res = DbModel.session.query(Holiday).filter(Holiday.country_id == i.country_id).filter(
                    Holiday.dt_utc_id == i.dt_utc_id).first()
                if not res:
                    logger.info(f"Nowy rekord: {i}")
                    DbModel.session.merge(i)
            DbModel.session.commit()
        except Exception as e:
            logger.error(e)
