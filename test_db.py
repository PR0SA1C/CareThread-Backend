import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()

# Get URL and fix postgres:// to postgresql:// if needed by sqlalchemy
url = os.getenv("DATABASE_URL")
if url and url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

try:
    engine = create_engine(url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("=== SUCCESS ===")
    print("Connected to the PostgreSQL Database!")
    print(f"Found {len(tables)} tables: {tables}")
except Exception as e:
    print("=== ERROR ===")
    print(f"Failed to connect: {e}")
