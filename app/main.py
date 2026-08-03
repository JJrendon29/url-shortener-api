from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import urls


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="URL Shortener API",
    description="Acortador de URLs con caché Redis, estadísticas y expiración automática",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(urls.router)
