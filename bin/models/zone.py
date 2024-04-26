from sqlalchemy import Column, Integer, String

from bin.models.db_model import DbModel


class Zone(DbModel.Model):
    __tablename__ = 'ENTSOE_zones'
    __table_args__ = {"schema": "dbo"}

    id = Column(Integer, primary_key=True)
    zone_name = Column(String)
    code = Column(String)
    meaning = Column(String)
    tz_ = Column(String)
    value = Column(String)

