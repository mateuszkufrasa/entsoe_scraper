from sqlalchemy import Column, Integer, DateTime, String

from bin.models.db_model import DbModel


class AllocatedCapacity(DbModel.Model):
    __tablename__ = 'ENTSOE_Allocated_Capacities'
    __table_args__ = {"schema": "dbo"}

    id = Column('Id', Integer, primary_key=True)
    dt = Column('Datetime', DateTime, nullable=False)
    unit = Column('Unit', String, nullable=False)
    country = Column('Country', String, nullable=False)
    code = Column('Code', String, nullable=False)
    fuel = Column('Fuel', String, nullable=False)
    generation = Column('Generation', Integer, nullable=True)