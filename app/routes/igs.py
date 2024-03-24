# app/routes/igs.py
import uuid
from fastapi import APIRouter, Depends, Query, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..utils import get_geodata_properties, get_geodata
from ..auth import authorize

router = APIRouter()

@router.get("/status")
def read_status():
  return { "status": "ok" }

@router.get("/")
def get_igs(simplified: str = Query("0.005"), includeProperties: bool = True, db: Session = Depends(get_db)):
  igs = db.query(models.DimbIg).filter(models.DimbIg.simplified == simplified).all()
  features = []
  for row in igs:
    meta = row.meta
    meta["postcodes"] = row.postcodes
    feature = {
        "type": "Feature",
        "properties": meta,
        "geometry": row.geometry
    }
    features.append(feature)

  if (includeProperties == True):
    return get_geodata_properties(features)
  return {
    "type": "FeatureCollection",
    "features": features
  }

@router.get("/{name}")
def get_ig(name: str, simplified: str = Query("0.005"), includeProperties: bool = True, db: Session = Depends(get_db)):
  ig = db.query(models.DimbIg).filter(models.DimbIg.name == name, models.DimbIg.simplified == simplified).scalar()

  if not ig:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found")

  meta = ig.meta
  meta["postcodes"] = ig.postcodes
  features = []
  feature = {
    "type": "Feature",
    "properties": meta,
    "geometry": ig.geometry
  }
  features.append(feature)

  if (includeProperties == True):
    return get_geodata_properties(features)
  return {
    "type": "FeatureCollection",
    "features": features
  }

@router.post("/")
def update_ig(item: schemas.DimbIgInput, simplified: str = Query("0.005"), db: Session = Depends(get_db)):
  ig = db.query(models.DimbIg).filter(models.DimbIg.name == item.name, models.DimbIg.simplified == simplified).scalar()
  exists = ig

  if not ig:
    meta = {
      "name": item.name
    }
    ig = models.DimbIg(id=uuid.uuid4(), name=item.name, meta=meta, simplified=simplified)

  if item.postcodes:
    data = get_geodata(item, simplified)
    setattr(ig, "postcodes", item.postcodes)
    if data:
      setattr(ig, "geometry", jsonable_encoder(data))

  if item.meta:
    setattr(ig, "meta", item.meta)

  if not exists:
    db.add(ig)

  db.commit()
  db.refresh(ig)
  return ig

@router.put("/{name}")
def update_ig(name: str, item: schemas.DimbIgInput, simplified: str = Query("0.005"), db: Session = Depends(get_db)):
  ig = db.query(models.DimbIg).filter(models.DimbIg.name == name, models.DimbIg.simplified == simplified).scalar()

  if not ig:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found")

  if item.postcodes:
    data = get_geodata(item, simplified)
    setattr(ig, "postcodes", item.postcodes)
    if data:
      setattr(ig, "geometry", jsonable_encoder(data))

  if item.meta:
    setattr(ig, "meta", item.meta)

  db.commit()
  db.refresh(ig)
  return ig

@router.delete("/{name}")
def delete_ig(name: str, simplified: str = Query("0.005"), db: Session = Depends(get_db)):
  ig = db.query(models.DimbIg).filter(models.DimbIg.name == name, models.DimbIg.simplified == simplified).scalar()
  
  if not ig:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found")

  db.delete(ig)
  db.commit()
  return Response(status_code=status.HTTP_204_NO_CONTENT)
