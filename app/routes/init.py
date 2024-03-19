# app/routes/init.py
import requests
from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import authorize, signJWT
from ..config import settings

router = APIRouter()

@router.get("/")
def get_igs(db: Session = Depends(get_db)):
  query = text("SELECT * FROM dimb")
  results = db.execute(query)
  items = []
  for row in results:
    data = {
        "name": row.ig,
        "postcodes": row.plz.split(',')
    }
    items.append(data)

  return items

@router.post("/", dependencies=[Depends(authorize)])
def update_ig(simplified: str = Query("0.005"), db: Session = Depends(get_db)):
  api = settings.CACHE_API
  url = api + "/api/igs/?simplified=" + simplified
  token = signJWT(settings.USERNAME)
  if token:    
    headers = {
      "Accept": "application/json", 
      "Content-Type": "application/json", 
      "Authorization": "Bearer " + token["access_token"],
    }
    query = text("SELECT * FROM dimb")
    results = db.execute(query)
    for row in results:
      data = {
        "name": row.ig,
        "postcodes": row.plz.split(',')
      }
      payload = jsonable_encoder(data)
      requests.post(url, json=payload, headers=headers)

  return { "status": "Ok" }
