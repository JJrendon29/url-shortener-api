import json
import secrets
from datetime import datetime, timedelta
from typing import Optional
import redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from app.config import settings
from app.database import get_session
from app.models.url import URL
from app.schemas.url import URLCreate, URLResponse, URLStats

router = APIRouter(tags=["urls"])

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


def generate_unique_code(session: Session) -> str:
    while True:
        code = secrets.token_urlsafe(6)
        existing = session.exec(select(URL).where(URL.code == code)).first()
        if not existing:
            return code


def build_short_url(code: str) -> str:
    return f"{settings.base_url}/{code}"


def url_to_dict(url: URL, short_url: str) -> dict:
    return {
        "code": url.code,
        "original_url": str(url.original_url),
        "short_url": short_url,
        "clicks": url.clicks,
        "created_at": url.created_at.isoformat(),
        "expires_at": url.expires_at.isoformat()
    }


@router.post("/urls", response_model=URLResponse, status_code=201)
def create_url(url_data: URLCreate, session: Session = Depends(get_session)):
    code = generate_unique_code(session)
    expires_at = datetime.utcnow() + timedelta(hours=url_data.expires_in_hours)

    url = URL(
        original_url=str(url_data.original_url),
        code=code,
        expires_at=expires_at
    )
    session.add(url)
    session.commit()
    session.refresh(url)

    short_url = build_short_url(code)
    ttl_seconds = url_data.expires_in_hours * 3600
    redis_client.set(f"url:{code}", json.dumps(url_to_dict(url, short_url)), ex=ttl_seconds)

    return URLResponse(**url_to_dict(url, short_url))


@router.get("/{code}")
def redirect_url(code: str, session: Session = Depends(get_session)):
    cached = redis_client.get(f"url:{code}")

    if cached:
        data = json.loads(cached)
        redis_client.expire(f"url:{code}", 3600)
    else:
        url = session.exec(select(URL).where(URL.code == code)).first()
        if not url:
            raise HTTPException(status_code=404, detail="URL no encontrada")
        if url.expires_at < datetime.utcnow():
            raise HTTPException(status_code=410, detail="URL expirada")

        short_url = build_short_url(code)
        data = url_to_dict(url, short_url)
        ttl_remaining = int((url.expires_at - datetime.utcnow()).total_seconds())
        redis_client.set(f"url:{code}", json.dumps(data), ex=ttl_remaining)

    url = session.exec(select(URL).where(URL.code == code)).first()
    if url:
        url.clicks += 1
        session.add(url)
        session.commit()

    return RedirectResponse(url=data["original_url"], status_code=302)


@router.get("/urls/{code}/stats", response_model=URLStats)
def get_stats(code: str, session: Session = Depends(get_session)):
    url = session.exec(select(URL).where(URL.code == code)).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL no encontrada")
    if url.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="URL expirada")

    short_url = build_short_url(code)
    return URLStats(**url_to_dict(url, short_url))
