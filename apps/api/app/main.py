from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import Base, engine
from app.models import *
from app.api.routes import router

app = FastAPI(title="Market Monitor API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.api_cors_origins.split(",") if x.strip()], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

@app.on_event("startup")
def initialize_database():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"service": "market-monitor-api", "status": "ok", "docs": "/docs", "version": "0.2.0"}
