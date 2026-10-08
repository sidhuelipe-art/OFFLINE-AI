from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from .database import Base


class User(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    owner_email = Column(String, index=True, nullable=True)
    title = Column(String, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class FileMetadata(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    owner_email = Column(String, index=True, nullable=True)
    filename = Column(String)
    filepath = Column(String)
    file_type = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True, index=True)
    owner_email = Column(String, index=True, nullable=True)
    title = Column(String)
    due_date = Column(DateTime)
    completed = Column(Boolean, default=False)


class ChatMessage(Base):
    """A persisted message scoped to the signed-in email address."""

    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    owner_email = Column(String, index=True, nullable=True)
    role = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class SystemSetting(Base):
    __tablename__ = "settings"
    key = Column(String, primary_key=True, index=True)
    value = Column(String)
