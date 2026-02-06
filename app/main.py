from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select

from .db import engine, SessionLocal
from .models import Ping
from .user_model import User
from .session import get_session
from .auth_google import router as google_router
from .inventory_model import InventoryItem

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
        InventoryItem.metadata.create_all(bind=engine)

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

from fastapi import Form
from starlette.responses import RedirectResponse
from sqlalchemy import select

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    sess = get_session(request)
    if not sess:
        return "<h2>Please <a href='/auth/google/start'>sign in</a></h2>"

    user_id = sess["user_id"]

    with SessionLocal() as db:
        items = db.execute(
            select(InventoryItem).where(InventoryItem.user_id == user_id).order_by(InventoryItem.id.desc())
        ).scalars().all()

    # simple HTML (we’ll Jinja this later)
    rows = "".join(
        f"""
        <li>
          {i.name} — qty {i.quantity} — {i.location}
          <form action="/inventory/{i.id}/consume" method="post" style="display:inline;">
            <button type="submit">Consume 1</button>
          </form>
        </li>
        """
        for i in items
    )

    return f"""
    <h1>Dashboard</h1>
    <p>Hello {sess.get('name')} ({sess.get('email')})</p>

    <h3>Add item</h3>
    <form action="/inventory/add" method="post">
      <input name="name" placeholder="Milk" required />
      <input name="quantity" type="number" value="1" min="1" required />
      <select name="location">
        <option value="pantry">pantry</option>
        <option value="fridge">fridge</option>
        <option value="freezer">freezer</option>
      </select>
      <button type="submit">Add</button>
    </form>

    <h3>Your items</h3>
    <ul>{rows}</ul>

    <form action="/auth/logout" method="post">
      <button type="submit">Log out</button>
    </form>
    """

@app.post("/inventory/add")
def add_item(request: Request, name: str = Form(...), quantity: int = Form(1), location: str = Form("pantry")):
    sess = get_session(request)
    if not sess:
        return RedirectResponse(url="/", status_code=303)

    user_id = sess["user_id"]

    with SessionLocal() as db:
        db.add(InventoryItem(user_id=user_id, name=name.strip(), quantity=quantity, location=location))
        db.commit()

    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/inventory/{item_id}/consume")
def consume_item(request: Request, item_id: int):
    sess = get_session(request)
    if not sess:
        return RedirectResponse(url="/", status_code=303)

    user_id = sess["user_id"]

    with SessionLocal() as db:
        item = db.execute(
            select(InventoryItem).where(InventoryItem.id == item_id, InventoryItem.user_id == user_id)
        ).scalar_one_or_none()

        if item:
            item.quantity -= 1
            if item.quantity <= 0:
                db.delete(item)
            db.commit()

    return RedirectResponse(url="/dashboard", status_code=303)
