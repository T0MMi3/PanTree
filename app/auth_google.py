from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from sqlalchemy import select

from .config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, BASE_URL
from .db import SessionLocal
from .user_model import User
from .session import set_session, clear_session

router = APIRouter()

oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

@router.get("/auth/google/start")
async def google_start(request: Request):
    redirect_uri = f"{BASE_URL}/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo")

    # Fallback if userinfo missing
    if not userinfo:
        userinfo = await oauth.google.parse_id_token(request, token)

    google_sub = userinfo.get("sub")
    email = userinfo.get("email")
    name = userinfo.get("name")
    picture = userinfo.get("picture")

    with SessionLocal() as db:
        existing = db.execute(select(User).where(User.google_sub == google_sub)).scalar_one_or_none()
        if not existing:
            existing = User(
                google_sub=google_sub,
                email=email,
                name=name,
                picture_url=picture
            )
            db.add(existing)
            db.commit()
            db.refresh(existing)

    resp = RedirectResponse(url="/dashboard")
    set_session(resp, {"user_id": existing.id, "email": existing.email, "name": existing.name})
    return resp

@router.post("/auth/logout")
async def logout():
    resp = RedirectResponse(url="/", status_code=303)
    clear_session(resp)
    return resp
