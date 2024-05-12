from datetime import datetime

import pandas as pd
from loguru import logger
from sqlalchemy import Column, Integer, DateTime, ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import relationship

from bin.models.db_model import DbModel
from bin.models.failed_download import FailedDownload
from bin.models.zone import Zone
import dateutil.tz as dtz


class TotalLoadDayAheadForecast(DbModel.Model):
    __tablename__ = 'ENTSOE_total_load_da_fc'
    __table_args__ = {"schema": "dbo"}

    id = Column('Id', Integer, primary_key=True)
    dt_utc = Column('dt_utc', DateTime, nullable=False)
    dt_local = Column('dt_local', DateTime, nullable=False)
    zone_id = Column('zone', ForeignKey('dbo.ENTSOE_zones.id'))
    total_load = Column('total_load', DECIMAL, nullable=False)
    timestamp = Column('timestamp', DateTime, nullable=False)

    zone = relationship('Zone', backref='bid_zone', foreign_keys=[zone_id])

    @staticmethod
    def from_df(index_, row: pd.Series, bid_zone: Zone, tstamp: datetime):
        local_tz: str = bid_zone.country.tz_
        dt_utc = index_
        dt_local = dt_utc.astimezone(dtz.gettz(local_tz))
        total_load = row[0]
        return TotalLoadDayAheadForecast(dt_utc=dt_utc, dt_local=dt_local, zone_id=bid_zone.id, total_load=total_load,
                                         timestamp=tstamp)

    @staticmethod
    def insert_or_update(items: list) -> None:
        logger.info(f"Aktualizacja obiektów {__class__.__name__} w bazie")
        try:
            for i in items:
                res = DbModel.session.query(TotalLoadDayAheadForecast).filter(
                    TotalLoadDayAheadForecast.dt_utc == i.dt_utc).filter(
                    TotalLoadDayAheadForecast.zone_id == i.zone_id).first()
                if res:
                    res.dt_utc = i.dt_utc
                    res.dt_local = i.dt_local
                    res.total_load = i.total_load
                    res.timestamp = i.timestamp
                    DbModel.session.merge(res)
                    DbModel.session.commit()
                else:
                    logger.info(f"Nowy rekord: {i}")
                    DbModel.session.merge(i)
                    DbModel.session.commit()
        except Exception as e:
            logger.error(e)

    @staticmethod
    def on_error_save(dt_local, method, **kwargs):
        db_item = FailedDownload(dt_local=dt_local, method=method, params=str({**kwargs}))
        DbModel.session.add(db_item)
        DbModel.session.commit()
