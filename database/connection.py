import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# --------------------------------
# Load environment variables
# --------------------------------

load_dotenv()


# --------------------------------
# Get Database URL
# --------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set in the .env file."
    )


# --------------------------------
# Create Database Engine
# --------------------------------

engine = create_engine(
    DATABASE_URL
)


# --------------------------------
# Create Database Session
# --------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# --------------------------------
# Database Dependency
# --------------------------------

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


print("Database connection created successfully!")