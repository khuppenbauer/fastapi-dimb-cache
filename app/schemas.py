# schemas.py
from pydantic import BaseModel
from typing import List

class DimbIgInput(BaseModel):
  name: str
  postcodes: List = []
  logourl: str = ''
  siteurl: str = ''
  contact: str = ''
  activities: List = []
  description: str = ''
