from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select

from .db import engine, SessionLocal
from .models import Ping
from .user_model import User
from .session import get_session
from .auth_google import router as google_router

from starlette.middleware.sessions import SessionMiddleware
import os


app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "dev-secret-change-me"),
    same_site="lax",
    https_only=True,
)

app.include_router(google_router)

@app.on_event("startup")
def startup():
    if engine is not None:
        Ping.metadata.create_all(bind=engine)
        User.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    sess = get_session(request)

    if sess:
        return f"""
        <h1>PanTree 🌱</h1>
        <p>Logged in as {sess.get('email')}</p>
        <p><a href="/dashboard">Go to dashboard</a></p>
        <form action="/auth/logout" method="post">
            <button type="submit">Log out</button>
        </form>
        """

    return """
    <h1>PanTree 🌱</h1>
    <p><a href="/auth/google/start">Sign in with Google</a></p>
    """

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    sess = get_session(request)
    if not sess:
        return "<h2>Please <a href='/auth/google/start'>sign in</a></h2>"

    with SessionLocal() as db:
        db.add(Ping(message="dashboard"))
        db.commit()
        rows = db.execute(select(Ping)).all()

    return f"""
    <h1>Dashboard</h1>
    <p>Hello {sess.get('name')}</p>
    <p>Ping rows: {len(rows)}</p>
    """
