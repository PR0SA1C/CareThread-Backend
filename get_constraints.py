import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
if url and url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

engine = create_engine(url)
with engine.connect() as conn:
    res = conn.execute(text("SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid IN ('encounters'::regclass, 'conditions'::regclass, 'medications'::regclass)")).fetchall()
    for row in res:
        print(f"{row[0]}: {row[1]}")
