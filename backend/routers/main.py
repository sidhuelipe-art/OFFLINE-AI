import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text
from starlette.middleware.sessions import SessionMiddleware

from backend import models
from backend.database import Base, engine
from backend.routers import auth, chat, files, generate, memory, notes, reminders, settings, voice

Base.metadata.create_all(bind=engine)
with engine.begin() as connection:
    inspector = inspect(connection)
    for table in ("notes", "files", "reminders", "chat_history"):
        columns = {column["name"] for column in inspector.get_columns(table)}
        if "owner_email" not in columns:
            connection.execute(text(f"ALTER TABLE {table} ADD COLUMN owner_email VARCHAR"))
            connection.execute(text(f"CREATE INDEX IF NOT EXISTS ix_{table}_owner_email ON {table} (owner_email)"))

app = FastAPI(title="OFF AI Assistant API", version="1.0.0")

secret_key = os.getenv("SESSION_SECRET")
if not secret_key:
    if os.getenv("ENVIRONMENT", "development").lower() == "production":
        raise RuntimeError("SESSION_SECRET must be set in production.")
    secret_key = "development-only-change-me"

app.add_middleware(
    SessionMiddleware,
    secret_key=secret_key,
    same_site="lax",
    https_only=os.getenv("ENVIRONMENT", "development").lower() == "production",
)

allowed_hosts = [host.strip() for host in os.getenv("ALLOWED_HOSTS", "*").split(",") if host.strip()]
if allowed_hosts != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()]
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(files.router)
app.include_router(generate.router)
app.include_router(memory.router)
app.include_router(notes.router)
app.include_router(reminders.router)
app.include_router(settings.router)
app.include_router(voice.router)

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}

frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
if frontend_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
