from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(String, primary_key=True)
    last_seen = Column(DateTime, default=datetime.utcnow)

class Vehiculo(Base):
    __tablename__ = 'vehiculos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_id = Column(String, ForeignKey('tags.id'))
    matricula = Column(String)
    bastidor = Column(String)

class Posicion(Base):
    __tablename__ = 'posiciones'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_id = Column(String, ForeignKey('tags.id'))
    x = Column(Float)
    y = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Configuracion(Base):
    __tablename__ = 'configuraciones'
    tag_id = Column(String, ForeignKey('tags.id'), primary_key=True)
    sleep_interval_ms = Column(Integer)
    transmit_offset_ms = Column(Integer)
    channel = Column(Integer)
