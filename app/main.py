from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401 — needed so create_all sees the tables
from app.config import settings
from app.database import Base, engine
from app.routers import matches

app = FastAPI(title="Hoopsdata-api", version="0.1.0")


# create all table in my database
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # setting from where the api can be use
    allow_methods=["*"],  # setting wich methods can be use
    allow_headers=["*"],  # setting wich headers can be use
)

app.include_router(matches.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "hoopsdata-api"}
