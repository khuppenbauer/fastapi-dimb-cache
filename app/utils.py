# utils.py
import requests
from typing import List, Union, Dict
from fastapi.encoders import jsonable_encoder
from . import schemas
from .auth import signJWT
from .config import settings

GeoJsonFeatureType = Dict[str, Union[str, List[Union[str, List[Union[float, List[List[float]]]]]]]]

def get_geodata_properties(features: Dict[str, Union[str, List[Union[str, List[Union[float, List[List[float]]]]]]]]) -> GeoJsonFeatureType:
  featureCollection = {
    "type": "FeatureCollection",
    "features": features
  }

  url = settings.API + "/api/properties/"
  headers = {
    "Accept": "application/json", 
    "Content-Type": "application/json", 
  }
  token = signJWT(settings.USERNAME)
  if token:
    headers["Authorization"] = "Bearer " + token["access_token"]
  payload = jsonable_encoder(featureCollection)
  res = requests.post(url, json=payload, headers=headers)
  if res.status_code == 200:
    featureCollection["properties"] = res.json()

  return featureCollection

def get_geodata(item: schemas.DimbIgInput, simplified: str):
  url = settings.API + "/api/areas/?simplified=" + simplified
  payload = jsonable_encoder(item)
  headers = get_headers()
  res = requests.post(url, json=payload, headers=headers)
  if res.status_code == 200:
    return res.json()
  return

def get_headers():
  token = signJWT(settings.USERNAME)
  headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
  }
  if token:
    headers["Authorization"] = "Bearer " + token["access_token"]
  return headers
