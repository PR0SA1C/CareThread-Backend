import os
import uuid
import random
from datetime import datetime
from faker import Faker
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
if url and url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

engine = create_engine(url)

# Use the Indian locale for realistic names and addresses!
fake = Faker('en_IN')

NUM_FACILITIES = 3
NUM_PRACTITIONERS = 10
NUM_PATIENTS = 15

def seed():
    # Use begin() to automatically commit if successful
    with engine.begin() as conn:
        print("Starting Database Seed Process...")
        
        facilities_ids = []
        print(f"-> Generating {NUM_FACILITIES} Mock Facilities...")
        for _ in range(NUM_FACILITIES):
            fid = str(uuid.uuid4())
            facilities_ids.append(fid)
            conn.execute(
                text("""
                    INSERT INTO facilities (id, name, facility_type, abdm_facility_id, address, city, created_at)
                    VALUES (:id, :name, :ftype, :abdm_id, :address, :city, :created_at)
                """),
                {
                    "id": fid,
                    "name": fake.company() + " Hospital",
                    "ftype": None,
                    "abdm_id": f"IN-FAC-{random.randint(10000, 99999)}",
                    "address": fake.street_address(),
                    "city": fake.city(),
                    "created_at": datetime.utcnow()
                }
            )

        practitioner_ids = []
        print(f"-> Generating {NUM_PRACTITIONERS} Mock Practitioners...")
        for _ in range(NUM_PRACTITIONERS):
            pid = str(uuid.uuid4())
            practitioner_ids.append(pid)
            conn.execute(
                text("""
                    INSERT INTO practitioners (id, facility_id, full_name, specialty, abdm_hpr_id, created_at)
                    VALUES (:id, :fac_id, :full_name, :specialty, :abdm_id, :created_at)
                """),
                {
                    "id": pid,
                    "fac_id": random.choice(facilities_ids),
                    "full_name": "Dr. " + fake.name(),
                    "specialty": random.choice(["Cardiology", "Neurology", "General Practice", "Orthopedics", "Pathology"]),
                    "abdm_id": f"HPR-{random.randint(100000, 999999)}",
                    "created_at": datetime.utcnow()
                }
            )

        print(f"-> Generating {NUM_PATIENTS} Mock Patients with ABHA IDs...")
        for _ in range(NUM_PATIENTS):
            # Realistic 14-digit ABHA ID format: XX-XXXX-XXXX-XXXX
            abha = f"{random.randint(10,99)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
            conn.execute(
                text("""
                    INSERT INTO patients (id, abha_id, full_name, date_of_birth, gender, phone, blood_group, created_at, updated_at, address, email)
                    VALUES (:id, :abha, :name, :dob, :gender, :phone, :bg, :created_at, :updated_at, :address, :email)
                """),
                {
                    "id": str(uuid.uuid4()),
                    "abha": abha,
                    "name": fake.name(),
                    "dob": fake.date_of_birth(minimum_age=18, maximum_age=85),
                    "gender": None,
                    "phone": fake.phone_number(),
                    "bg": random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "address": fake.address(),
                    "email": fake.email()
                }
            )

        print("=== Seed Process Complete! ===")

if __name__ == "__main__":
    seed()
