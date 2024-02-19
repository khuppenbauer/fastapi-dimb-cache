# app/routes/token.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing_extensions import Annotated
from ..auth import signJWT, verifyUser

router = APIRouter()

@router.post("/token")
def login_for_access_token(
  form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
  user = verifyUser(form_data.username, form_data.password)
  if not user:
    raise HTTPException(status_code=400, detail="Incorrect username or password")
  return signJWT(form_data.username)
