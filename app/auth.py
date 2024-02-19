# app/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from typing_extensions import Annotated
from .config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
USERNAME = settings.USERNAME
PASSWORD= settings.PASSWORD

oauth2_scheme = OAuth2PasswordBearer(
  tokenUrl="token",
)

def token_response(token: str):
  return {
    "access_token": token,
    "token_type": "bearer",
  }

def verifyUser(username: str, password: str) -> bool:
  if username == USERNAME and password == PASSWORD:
    return True
  return False

def signJWT(user_id: str) -> dict:
  payload = {
    "user": user_id,
  }
  token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
  return token_response(token)

def decodeJWT(token: str) -> dict:
  try:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
  except:
    return {}

def authorize(token: Annotated[str, Depends(oauth2_scheme)]):
  authenticate_value = "Bearer"
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": authenticate_value},
  )
  try:
    payload = decodeJWT(token)
    user: str = payload.get("user")
    if user is None:
      raise credentials_exception
  except (JWTError, ValidationError):
    raise credentials_exception
