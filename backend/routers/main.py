from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from database import engine, Base
from routers import auth, chat, files, generate, memory, notes, reminders, settings, voice
import models  # noqa: F401 - registers all tables before create_all


# Existing SQLite databases need a safe, additive migration for email ownership.
Base.metadata.create_all(bind=engine)
with engine.begin() as connection:
    inspector = inspect(engine)
    for table in ("notes", "files", "reminders", "chat_history"):
        columns = {column["name"] for column in inspect(connection).get_columns(table)}
        if "owner_email" not in columns:
            connection.execute(text(f"ALTER TABLE {table} ADD COLUMN owner_email VARCHAR"))
            connection.execute(text(f"CREATE INDEX IF NOT EXISTS ix_{table}_owner_email ON {table} (owner_email)"))
    # The old global memory table is obsolete and must not be exposed.
    connection.execute(text("DROP TABLE IF EXISTS memory"))

app = FastAPI(title="OFF AI Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
