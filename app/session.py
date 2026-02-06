from itsdangerous import URLSafeSerializer
from fastapi import Request, Response
from .config import SESSION_SECRET

_serializer = URLSafeSerializer(SESSION_SECRET, salt="pantree-session")

COOKIE_NAME = "pantree_session"

def set_session(response: Response, data: dict):
    token = _serializer.dumps(data)
    response.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        secure=True,      # Render is HTTPS
        samesite="lax",
        max_age=60 * 60 * 24 * 14,  # 14 days
    )

def clear_session(response: Response):
    response.delete_cookie(COOKIE_NAME)

def get_session(request: Request) -> dict | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        return _serializer.loads(token)
    except Exception:
        return None
