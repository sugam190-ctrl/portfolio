"""
This file sets up the connection between SQLAlchemy (Python) and the actual
database (SQLite locally, Postgres in production).

Think of it as the "wire" that every other file plugs into to talk to the DB.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()  # reads variables from .env into the environment

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./portfolio.db")

# connect_args is only needed for SQLite (it doesn't allow multi-thread
# access by default, and FastAPI is async/multi-threaded).
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# SessionLocal is a factory that creates new DB sessions (like opening
# a "conversation" with the database for a single request).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the class every one of our table models will inherit from.
# SQLAlchemy uses this to know which Python classes map to which SQL tables.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency: gives each request its own DB session and
    guarantees it's closed afterward, even if an error happens.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
