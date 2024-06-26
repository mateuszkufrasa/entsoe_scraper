import awoc
from entsoe import Area
from loguru import logger
from sqlalchemy import Column, Integer, String

from bin.models.db_model import DbModel


class Country(DbModel.Model):
    __tablename__ = 'ENTSOE_countries'
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    iso2 = Column(String)
    tz_ = Column(String)

    # TODO: repr

    @staticmethod
    def generate() -> list:
        _countries = awoc.AWOC()
        countries_of_europe = _countries.get_countries()
        time_zones = {a.tz for a in Area}
        logger.debug(f"Generowanie obiektów {__class__.__name__}")
        out = []
        for t in time_zones:
            res = [i['Country Name'] for i in countries_of_europe if i['Time Zone in Capital'] == t]
            if t in ['Europe/Kaliningrad', 'Europe/Moscow']:
                out.append(Country(name='Russia', tz_=t, iso2='RU'))
            elif t == 'Europe/Belfast':
                out.append(Country(name='Northern Ireland', tz_=t, iso2='GB'))
            else:
                if len(res) > 1:
                    res.remove('Kosovo')
                elif len(res) == 0:
                    continue
                country_iso2 = _countries.get_country_ISO2(res[0])
                out.append(Country(name=res[0], tz_=t, iso2=country_iso2))
        return out

    @staticmethod
    def insert_or_update(items: list) -> None:
        logger.info(f"Aktualizacja obiektów {__class__.__name__} w bazie")
        try:
            for i in items:
                res = DbModel.session.query(Country).filter(Country.name == i.name).first()
                if res:
                    res.name = i.name
                    res.tz_ = i.tz_
                    DbModel.session.merge(res)
                else:
                    logger.info(f"Nowy rekord: {i}")
                    DbModel.session.merge(i)
            DbModel.session.commit()
        except Exception as e:
            logger.error(e)
