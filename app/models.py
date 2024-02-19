# models.py
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy import Column, String, Double
from .database import Base

class DimbIg(Base):
  __tablename__ = 'dimb_ig'

  id = Column(primary_key=True)
  name = Column(String(255), nullable=False)
  meta = Column(JSON)
  geometry = Column(JSON)
  simplified = Column(Double)
