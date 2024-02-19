# app/routes/igs.py
import json
import requests
import uuid
from fastapi import APIRouter, Depends, Query, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..auth import authorize, signJWT
from ..config import settings

router = APIRouter()

@router.get("/")
def get_igs(simplified: str = Query("0.005"), db: Session = Depends(get_db)):
  igs = db.query(models.DimbIg).filter(models.DimbIg.simplified == simplified).all()
  geometries = []
  features = []
  for row in igs:
    geometries.append(row.geometry)
    feature = {
        "type": "Feature",
        "properties": row.meta,
        "geometry": row.geometry
    }
    features.append(feature)

  geometryCollection = {
    "type": "GeometryCollection",
    "geometries": geometries
  }

  return {
    "type": "FeatureCollection",
    "features": features
  }

@router.get("/status")
def read_status():
  return {"status": "ok"}

@router.get("/{name}")
def get_ig(name: str, simplified: str = Query("0.005"), db: Session = Depends(get_db)):
  ig = db.query(models.DimbIg).filter(models.DimbIg.name == name, models.DimbIg.simplified == simplified).scalar()

  if not ig:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found")

  return ig


@router.post("/", dependencies=[Depends(authorize)])
def update_ig(item: schemas.DimbIgInput, simplified: str = Query("0.005"), db: Session = Depends(get_db)):
  ig = db.query(models.DimbIg).filter(models.DimbIg.name == item.name, models.DimbIg.simplified == simplified).scalar()
  api = settings.API
  url = api + "/api/igs/?simplified=" + simplified
  token = signJWT(settings.USERNAME)
  if token:    
    headers = {
      "Accept": "application/json", 
      "Content-Type": "application/json", 
      "Authorization": "Bearer " + token["access_token"],
    }
    payload = jsonable_encoder(item)
    res = requests.post(url, json=payload, headers=headers)
    if res.status_code == 200:
      data = res.json()
      if not ig:
        ig = models.DimbIg(id=uuid.uuid4(), name=item.name, simplified=simplified, meta=data["meta"])
        ig.geometry = jsonable_encoder(data["geometry"])
        db.add(ig)
      else:
        setattr(ig, "meta", data["meta"])
        setattr(ig, "geometry", jsonable_encoder(data["geometry"]))
      db.commit()
      db.refresh(ig)
  return ig


@router.put("/{name}", dependencies=[Depends(authorize)])
def update_ig(name: str, item: schemas.DimbIgInput, simplified: str = Query("0.005"), db: Session = Depends(get_db)):
  ig = db.query(models.DimbIg).filter(models.DimbIg.name == name, models.DimbIg.simplified == simplified).scalar()

  if not ig:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found")

  api = settings.API
  url = api + "/api/igs/?simplified=" + simplified
  token = signJWT(settings.USERNAME)
  if token:    
    headers = {
      "Accept": "application/json", 
      "Content-Type": "application/json", 
      "Authorization": "Bearer " + token["access_token"],
    }
    payload = jsonable_encoder(item)
    res = requests.post(url, json=payload, headers=headers);
    if res.status_code == 200:
      setattr(ig, "meta", res["meta"])
      setattr(ig, "geometry", jsonable_encoder(res["geometry"]))
      db.commit()
      db.refresh(ig)
  return ig


@router.delete("/{name}", dependencies=[Depends(authorize)])
def delete_ig(name: str, simplified: str = Query("0.005"), db: Session = Depends(get_db)):
  ig = db.query(models.DimbIg).filter(models.DimbIg.name == name, models.DimbIg.simplified == simplified).scalar()
  
  if not ig:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found")

  db.delete(ig)
  db.commit()
  return Response(status_code=status.HTTP_204_NO_CONTENT)