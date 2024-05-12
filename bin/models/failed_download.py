from sqlalchemy import Column, Integer, DateTime, String

from bin.models.db_model import DbModel


class FailedDownload(DbModel.Model):
    __tablename__ = 'ENTSOE_failed_actions'
    __table_args__ = {"schema": "dbo"}

    id = Column('Id', Integer, primary_key=True)
    dt_local = Column('dt_local', DateTime, nullable=False)
    method = Column('method', String, nullable=False)
    params = Column('params', String, nullable=False)

