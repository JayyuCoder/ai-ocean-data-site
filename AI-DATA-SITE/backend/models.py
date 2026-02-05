from sqlalchemy import Column, Integer, Float, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OceanMetrics(Base):
    __tablename__ = "ocean_metrics"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    latitude = Column(Float)
    longitude = Column(Float)
    sst = Column(Float)
    dhw = Column(Float)
    ph = Column(Float, nullable=True)
    health_score = Column(Float)
    anomaly = Column(Boolean)
    forecast_ph = Column(Float, nullable=True)
