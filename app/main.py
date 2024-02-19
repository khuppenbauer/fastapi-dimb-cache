# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import igs, token

app = FastAPI()

app.include_router(igs.router, prefix='/api/igs')
app.include_router(token.router)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.get("/")
def read_root():
  return {
    "message": "Welcome to the FastAPI project!"
  }
