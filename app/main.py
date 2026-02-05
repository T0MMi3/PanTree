from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .db import engine, SessionLocal
from .models import Ping
from sqlalchemy import select

app = FastAPI()

@app.on_event("startup")
def startup():
    # create tables on startup (okay for MVP)
    if engine is not None:
        Ping.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
def home():
    if SessionLocal is None:
        return "<h1>PanTree is live, but DATABASE_URL is not set.</h1>"

    with SessionLocal() as db:
        db.add(Ping(message="pong"))
        db.commit()

        count = db.execute(select(Ping)).all()
        return f"<h1>PanTree is live 🌱</h1><p>DB rows: {len(count)}</p>"
