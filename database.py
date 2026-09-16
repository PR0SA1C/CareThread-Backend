import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Example: postgresql://postgres:password@localhost:5432/carethread
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    print("WARNING: DATABASE_URL is not set in the .env file")

# Create engine
# If you are using psycopg2, the URL must start with postgresql://
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    print(f"Error initializing database engine: {e}")
    engine = None
    SessionLocal = None
    Base = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
