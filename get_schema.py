import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
if url and url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

engine = create_engine(url)
inspector = inspect(engine)

for table in ['org_staff', 'role_permissions']:
    print(f"\n--- Schema for: {table} ---")
    for col in inspector.get_columns(table):
        print(f"{col['name']} ({col['type']}) - nullable: {col['nullable']}")
