# app/routes/init.py
import requests
from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import authorize
from ..config import settings
from ..utils import get_headers

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

@router.post("/metadata")
def update_meta(simplified: str = Query("0.005")):
  cacheUrl = settings.CACHE_API + "/api/igs/?simplified=" + simplified
  headers = get_headers()

  metadataUrl = settings.METADATA_API
  res = requests.get(metadataUrl)
  json = res.json()
  for row in json["areas"]:
    data = {
      "name": "DIMB " + row['name'],
      "meta": row
    }
    payload = jsonable_encoder(data)
    requests.post(cacheUrl, json=payload, headers=headers)
  return { "status": "Ok" }

@router.post("/")
def update_ig(simplified: str = Query("0.005"), db: Session = Depends(get_db)):
  cacheUrl = settings.CACHE_API + "/api/igs/?simplified=" + simplified
  headers = get_headers()

  query = text("SELECT * FROM dimb")
  results = db.execute(query)
  for row in results:
    data = {
      "name": row.ig,
      "postcodes": row.plz.split(',')
    }
    payload = jsonable_encoder(data)
    requests.post(cacheUrl, json=payload, headers=headers)
  return { "status": "Ok" }
