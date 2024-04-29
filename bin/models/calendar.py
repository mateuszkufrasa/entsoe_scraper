from datetime import datetime

from dateutil.rrule import rrule, MINUTELY
from dateutil.tz import tz
from loguru import logger
from sqlalchemy import Column, Integer, DateTime, String

from bin.models.db_model import DbModel


# TODO: generate calendar with id, utc, local_time, frequency: 15 min up to year ahead
class Calendar(DbModel.Model):
    __tablename__ = 'Calendar'
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True)
    dt_utc = Column(DateTime, nullable=False)
    dt_local = Column(DateTime, nullable=False)
    tz_ = Column(String, nullable=False)

    def __repr__(self):
        return f"Calendar dt_utc={self.dt_utc}, dt_local={self.dt_local}, tz_={self.tz_}"

    @staticmethod
    def generate(dt_from: datetime, dt_to: datetime, tz_name: str) -> list:
        dts = []
        # wygeneruj listę datetime z zadanym interwałem
        dts_utc = list(rrule(MINUTELY, interval=15, dtstart=dt_from, until=dt_to))
        try:
            to_zone = tz.gettz(tz_name)
        except Exception as e:
            logger.error(e)
            logger.debug("Domyślna lokalna strefa czasowa: UTC")
            to_zone = tz.tzutc
        for dt in dts_utc:
            dt_local = dt.astimezone(to_zone)
            item = Calendar(dt_utc=dt, dt_local=dt_local, tz_=tz_name)
            dts.append(item)
        return dts

    @staticmethod
    #TODO: optimize
    def insert_or_update(items: list) -> None:
        logger.info(f"Aktualizacja obiektów Calendar w bazie")
        try:
            for i in items:
                res = DbModel.session.query(Calendar).filter(Calendar.dt_utc == i.dt_utc).first()
                if res:
                    res.dt_utc = i.dt_utc
                    res.dt_local = i.dt_local
                    res.tz_ = i.tz_
                    DbModel.session.merge(res)
                    DbModel.session.commit()
                else:
                    logger.info(f"Nowy rekord: {i}")
                    DbModel.session.merge(i)
                    DbModel.session.commit()
        except Exception as e:
            logger.error(e)
