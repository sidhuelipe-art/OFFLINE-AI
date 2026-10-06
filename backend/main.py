"""Application entrypoint.

The API is defined in routers/main.py; this wrapper keeps the existing
``python main.py`` and ``uvicorn main:app`` launch commands working while
ensuring chat history is persisted in SQLite.
"""

from routers.main import app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
